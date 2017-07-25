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

options (Optional): Select what level of address information you want. Choices are 'street', 'city', 'both', 'state' or 'country'. The default is “street"

### Example with optional entry for configuration.yaml
```
- platform: google_geocode
  name: michael
  origin: device_tracker.mobile_phone
  options: both
```
