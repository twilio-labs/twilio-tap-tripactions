# tap-tripactions

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from TripActions API -> https://support.tripactions.com/s/article/tripactions-booking-api 
More documentation about the API can be found here --> https://app.tripactions.com/api/public/documentation/swagger-ui/index.html?configUrl=/api/public/documentation/api-docs/swagger-config
- Extracts the following resources:
  - Booking API
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

# tap-tripaction
