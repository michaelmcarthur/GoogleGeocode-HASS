# Google Geocode

This component has been created to be used with Home Assistant.

Google geocode is the process of converting device tracker location into a human-readable address.

You need to register for an API key by following the instructions [here](https://github.com/googlemaps/google-maps-services-python#api-keys). You only need to turn on the Geocoding API

A free API Key allows 2500 requests per day. The sensor will update the address each time the device tracker location changes. If the device tracker is in a zone it will display the zone.

### Installation:

Copy the google_geocode.py file and place it in <config_dir>/custom_components/sensor/google_geocode.py.

### Example Screenshot:
![alt text](https://github.com/michaelmcarthur/GoogleGeocode-HASS/blob/master/Google_Geocode_Screenshot.png "Screenshot")

### Example entry for configuration.yaml
```
sensor:

  - platform: google_geocode
    api_key: XXXX_XXXXX_XXXXX
    origin: device_tracker.mobile_phone
```
### Configuration variables:

api_key (Required): Your application’s API key (get one by following the instructions above). This key identifies your application for purposes of quota management.

origin (Required): Tracking can be setup to track entity type device_tracker. Then every 5 minutes when the component updates it will use the latest location of that entity.

name (Optional): A name to display on the sensor. The default is “Google Geocode"

options (Optional): Select what level of address information you want. Choices are 'street', 'city', or 'both'. The default is “street"

### Example with optional entry for configuration.yaml
```
- platform: google_geocode
  name: michael
  api_key: XXXX_XXXXX_XXXXX
  origin: device_tracker.mobile_phone
  options: both
```
