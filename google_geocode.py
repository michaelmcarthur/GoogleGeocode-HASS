"""
Support for Google Geocode sensors.

For more details about this platform, please refer to the documentation at
https://github.com/michaelmcarthur/GoogleGeocode-HASS
"""
from datetime import datetime
from datetime import timedelta 
import json
import requests
from requests import get

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, CONF_SCAN_INTERVAL, ATTR_ATTRIBUTION, ATTR_LATITUDE, ATTR_LONGITUDE)
import homeassistant.helpers.location as location
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

CONF_ORIGIN = 'origin'
CONF_OPTIONS = 'options'

ATTR_STREET = 'Street'
ATTR_CITY = 'City'
ATTR_POSTAL_TOWN = 'Postal Town'
ATTR_POSTAL_CODE = 'Postal Code'
ATTR_REGION = 'State'
ATTR_COUNTRY = 'Country'
ATTR_FORMATTED_ADDRESS = 'Formatted Address'

DEFAULT_NAME = 'Google Geocode'
DEFAULT_OPTION = 'street'
current = '0,0'
zone_check = 'a'
SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_ORIGIN): cv.string,
    vol.Optional(CONF_OPTIONS, default=DEFAULT_OPTION): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL):
        cv.time_period,
})

TRACKABLE_DOMAINS = ['device_tracker']

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    name = config.get(CONF_NAME)
    api_key = config.get(CONF_API_KEY)
    origin = config.get(CONF_ORIGIN)
    options = config.get(CONF_OPTIONS)

    add_devices([GoogleGeocode(hass, origin, name, api_key, options)])
    

class GoogleGeocode(Entity):
    """Representation of a Google Geocode Sensor."""

    def __init__(self, hass, origin, name, api_key, options):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._options = options
        self._api_key = api_key
        self._state = None
        
        self._street = None
        self._city = None
        self._postal_town = None
        self._postal_code = None
        self._city = None
        self._region = None
        self._country = None
        self._formatted_address = None
        
        # self._origin = origin
        # Check if origin is a trackable entity
        if origin.split('.', 1)[0] in TRACKABLE_DOMAINS:
            self._origin_entity_id = origin
        else:
            self._origin = origin
            
        
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
        
    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return{
            ATTR_STREET: self._street,
            ATTR_CITY: self._city,
            ATTR_POSTAL_TOWN: self._postal_town,
            ATTR_POSTAL_CODE: self._postal_code,
            ATTR_REGION: self._region,
            ATTR_COUNTRY: self._country,
            ATTR_FORMATTED_ADDRESS: self._formatted_address,
        }
        
    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Get the latest data and updates the states."""
        
        if hasattr(self, '_origin_entity_id'):
            self._origin = self._get_location_from_entity(
                self._origin_entity_id
            )
        
        """Update if location has changed."""
        
        global current
        global zone_check
        zone_check = self.hass.states.get(self._origin_entity_id).state
        
        if zone_check == 'not_home':
            if current == self._origin:
                pass
            else:
                lat = self._origin
                current = lat
                api = self._api_key
                street = None
                city = None
                postal_town = None
                city = None
                state = None
                country = None
                self._street = None
                self._city = None
                self._postal_town = None
                self._postal_code = None
                self._city = None
                self._region = None
                self._country = None
                self._formatted_address = None
                url2 = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + lat + "&result_type=street_address" + "&key=" + api
                response = get(url2)
                json_input = response.text
                decoded = json.loads(json_input)
                for result in decoded["results"]:
                    for component in result["address_components"]:
                      if 'route' in component["types"]:
                          street = component["long_name"]
                          self._street = street
                      if 'locality' in component["types"]:
                          city = component["long_name"]
                          self._city = city
                      if 'postal_town' in component["types"]:
                          postal_town = component["long_name"]
                          self._postal_town = postal_town
                      if 'administrative_area_level_1' in component["types"]:
                          state = component["long_name"]
                          self._region = state
                      if 'country' in component["types"]:
                          country = component["long_name"]
                          self._country = country
                      if 'postal_code' in component["types"]:
                          postal_code = component["long_name"]
                          self._postal_code = postal_code
                          
                formatted_address = decoded['results'][0]['formatted_address']
                self._formatted_address = formatted_address
                if self._options == 'street':
                    ADDRESS = street
                elif self._options == 'city':
                    ADDRESS = city
                elif self._options == 'both':
                    ADDRESS = street + ", " + city
                elif self._options == 'full':
                    ADDRESS = formatted_address
                elif self._options == 'state':
                    ADDRESS = state
                elif self._options == 'country':
                    ADDRESS = country
                    
                self._state = ADDRESS
                
        else:
            self._state = zone_check[0].upper() + zone_check[1:]


    def _get_location_from_entity(self, entity_id):
        """Get the origin from the entity state or attributes."""
        entity = self._hass.states.get(entity_id)
        
        
        if entity is None:
            _LOGGER.error("Unable to find entity %s", entity_id)
            self.valid_api_connection = False
            return None

        # Check if the entity has origin attributes
        if location.has_location(entity):
            return self._get_location_from_attributes(entity)

        # When everything fails just return nothing
        return None
        
    @staticmethod
    def _get_location_from_attributes(entity):
        """Get the lat/long string from an entities attributes."""
        attr = entity.attributes
        return "%s,%s" % (attr.get(ATTR_LATITUDE), attr.get(ATTR_LONGITUDE))
