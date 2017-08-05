# Google Geocode

This component has been created to be used with Home Assistant.

Google geocode is the process of converting device tracker location into a human-readable address.

The sensor will update the address each time the device tracker location changes. If the device tracker is in a zone it will display the zone.

### Installation:

Copy the google_geocode.py file and place it in <config_dir>/custom_components/sensor/google_geocode.py.

### Example Screenshot:
![alt text](https://github.com/michaelmcarthur/GoogleGeocode-HASS/blob/master/Google_Geocode_Screenshot.png "Screenshot")

### Example entry for configuration.yaml
```
sensor:

  - platform: google_geocode
    origin: device_tracker.mobile_phone
```
### Configuration variables:

origin (Required): Tracking can be setup to track entity type device_tracker. The component updates it will use the latest location of that entity and update the sensor.

name (Optional): A name to display on the sensor. The default is “Google Geocode"

options (Optional): Select what level of address information you want. Choices are 'street_number', 'street', 'city', 'county', 'state', 'postal_code', 'country' or 'formatted_address'. You can use any combination of these options, separate each option with a comma. The default is “street, city"

display_zone (Optional): Choose to display a zone when in a zone. Choices are 'show' or 'hide'. The default is 'show'

gravatar (Optional): An email address for the device’s owner. You can set up a Gravatar [here.](https://gravatar.com) If provided, it will override `picture` The default is 'none'

api_key (Optional): Your application’s API key (get one by following the instructions below). This key identifies your application for purposes of quota management. Most users will not need to use this unless multiple sensors are created.

You need to register for an API key if you recieve a `OVER_QUERY_LIMIT` error. This can be done by following the instructions [here](https://github.com/googlemaps/google-maps-services-python#api-keys). You only need to turn on the Geocoding API. A free API Key allows 2500 requests per day. 

### Example with optional entry for configuration.yaml
```
- platform: google_geocode
  name: michael
  origin: device_tracker.mobile_phone
  options: street_number, street, city
  display_zone: hide
  gravatar: youremail@address.com
  api_key: XXXX_XXXXX_XXXXX
```
