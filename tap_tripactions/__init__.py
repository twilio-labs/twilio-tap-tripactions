#!/usr/bin/env python3
import singer
from singer import utils
from singer.catalog import Catalog, CatalogEntry
from tap_tripactions.streams import STREAMS, Stream

REQUIRED_CONFIG_KEYS = ["client_id", "client_secret", "start_date"]
LOGGER = singer.get_logger()


def discover():
    streams = []
    for stream in STREAMS.values():
        stream = stream()
        streams.append(
            CatalogEntry(
                tap_stream_id=stream.name,
                stream=stream.name,
                schema=stream.load_schemas(),
                key_properties=stream.key_properties,
                metadata=stream.load_metadata(),
                replication_key=stream.replication_key,
                replication_method=stream.replication_method,
            )
        )
    return Catalog(streams)


def sync(config, state, catalog):
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)
        streams_obj = streams.STREAMS.get(stream.tap_stream_id)
        streams_obj = streams_obj(config=config)

        singer.write_schema(
            stream_name=streams_obj.tap_stream_id,
            schema=streams_obj.load_schemas().to_dict(),
            key_properties=streams_obj.key_properties,
        )

        records_processed = streams_obj.do_sync(state, stream)
        LOGGER.info("%s: Completed sync (%s rows)", stream.tap_stream_id, records_processed)
    return


@utils.handle_top_exception(LOGGER)
def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # Discover flag mode
    if args.discover:
        catalog = discover()
        catalog.dump()
    # Catalog Mode
    elif args.catalog:
        catalog = args.catalog
        sync(args.config, args.state, catalog)


if __name__ == "__main__":
    main()
