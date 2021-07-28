import singer
import json
import os
from singer import metadata
from singer import utils
from singer.schema import Schema
from tap_tripactions import client
from datetime import datetime
import time
import simplejson

LOGGER = singer.get_logger()
KEY_PROPERTIES = ["uuid"]


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


class Stream:
    name = None
    replication_method = None
    replication_key = None
    key_properties = KEY_PROPERTIES
    stream = None
    schema = None

    def __init__(self, config=None):
        self.config = config

    def get_bookmark(self, state):
        if state:
            return round(
                utils.strptime_with_tz(state.get(self.name)).timestamp())
        else:
            return 0

    def load_schemas(self):
        schema_file = "schemas/{}.json".format(self.name)
        with open(get_abs_path(schema_file)) as f:
            schema = Schema.from_dict(json.load(f))
        return schema

    def load_metadata(self):
        mdata = metadata.new()
        mdata = metadata.write(mdata, (), 'table-key-properties', self.key_properties)
        mdata = metadata.write(mdata, (), 'forced-replication-method', self.replication_method)
        if self.replication_key:
            mdata = metadata.write(mdata, (), 'valid-replication-keys', [self.replication_key])
        return metadata.to_list(mdata)


class Bookings(Stream):
    name = "bookings"
    tap_stream_id = "bookings"
    replication_method = "INCREMENTAL"
    replication_key = "created"
    size = 100
    def do_sync(self, state, stream):
        LOGGER.info("Starting sync")
        if stream.replication_method == "INCREMENTAL":
            bookmark = self.get_bookmark(state=state)
        else:
            bookmark = 0

        trip_action_client = client.OAuth2Client(client_id=self.config["client_id"],
                                                 client_secret=self.config["client_secret"])

        if bookmark > round(datetime.strptime(self.config["start_date"], "%Y-%m-%d").timestamp()):
            created_from = bookmark
        else:
            created_from = round(datetime.strptime(self.config["start_date"], "%Y-%m-%d").timestamp())

        if "end_date" in self.config:
            end_date = round(datetime.strptime(self.config["end_date"], "%Y-%m-%d").timestamp())
        else:
            end_date = round(time.time())

        num_elements_processed_main = 0

        result = trip_action_client.get_booking_records(created_from=created_from, created_to=end_date, page=0,
                                                        size=self.size)
        num_elements = result.json()['page']['totalElements']
        while num_elements_processed_main < num_elements:
            num_elements_processed, created_from = self.get_records(trip_action_client=trip_action_client,
                                                                    created_from=created_from, end_date=end_date,
                                                                    stream=stream)
            num_elements_processed_main = num_elements_processed_main+num_elements_processed
        return num_elements_processed_main

    def get_records(self, trip_action_client, created_from, end_date, stream):

        bookmark_column = stream.replication_key
        result = trip_action_client.get_booking_records(created_from=created_from, created_to=end_date, page=0,
                                                        size=self.size)
        num_pages = result.json()['page']['totalPages']
        num_elements_processed = 0
        for page in range(0, num_pages):
            result = trip_action_client.get_booking_records(created_from=created_from, created_to=end_date, page=page,
                                                            size=self.size)
            try:
                for data in (result.json()['data']):
                    num_elements_processed = num_elements_processed + 1
                    singer.write_record(self.tap_stream_id, data)
                    if stream.replication_method == "INCREMENTAL":
                        singer.write_state({self.tap_stream_id: result.json()['data'][len(result.json()['data']) - 1][
                            bookmark_column]})
                        next_start_date = result.json()['data'][len(result.json()['data']) - 1][
                            bookmark_column]
            except simplejson.scanner.JSONDecodeError:
                LOGGER.info("End of Data Stream reached " + str(page) + " " + str(num_pages))
                break
            except Exception as e:
                if result.json()['status'] == 500:
                    LOGGER.info("Missing page in stream " + str(page))
                    num_elements_processed = num_elements_processed + self.size
                    continue
        return num_elements_processed, round(utils.strptime_with_tz(next_start_date).timestamp())


STREAMS = {"bookings": Bookings}
