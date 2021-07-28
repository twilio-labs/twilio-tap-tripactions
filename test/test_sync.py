import unittest
import tap_tripactions.streams as streams
import tap_tripactions
import json
import singer

with open("./test/secrets/secret_tripactions.json") as f:
    secret = json.load(f)
client_id = secret['client_id']
client_secret = secret["client_secret"]

config = {"start_date": "2018-08-13", "client_id": client_id, "client_secret": client_secret, "end_date" :"2018-09-05"}
streams_discover = tap_tripactions.discover()
LOGGER = singer.get_logger()

class TestSync(unittest.TestCase):
    def test_sync(self):

        stream = streams_discover.get_stream("bookings")
        print("Syncing stream:" + stream.tap_stream_id)
        streams_obj = streams.STREAMS.get(stream.tap_stream_id)
        streams_obj = streams_obj(config=config)

        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=stream.schema.to_dict(),
            key_properties=stream.key_properties,
        )

        records_processed = streams_obj.do_sync(None, stream)
        LOGGER.info("%s: Completed sync (%s rows)", stream.tap_stream_id, records_processed)

        self.assertTrue(records_processed)