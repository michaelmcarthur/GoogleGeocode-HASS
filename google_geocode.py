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
    CONF_API_KEY, CONF_NAME, ATTR_ATTRIBUTION, ATTR_LATITUDE, ATTR_LONGITUDE)
import homeassistant.helpers.location as location
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

CONF_ORIGIN = 'origin'
CONF_OPTIONS = 'options'


DEFAULT_NAME = 'Google Geocode'
DEFAULT_OPTION = 'street'
current = '0,0'
zone_check = 'a'
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_ORIGIN): cv.string,
    vol.Optional(CONF_OPTIONS, default=DEFAULT_OPTION): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
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

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
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
                url2 = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + lat + "&result_type=street_address" + "&key=" + api
                response = get(url2)
                json_input = response.text
                decoded = json.loads(json_input)
                street = decoded['results'][0]['address_components'][1]['long_name']
                city = decoded['results'][0]['address_components'][2]['long_name']
                if self._options == 'street':
                    ADDRESS = street
                elif self._options == 'city':
                    ADDRESS = city
                elif self._options == 'both':
                    ADDRESS = street + ", " + city
                    
                self._state = ADDRESS
        else:
            self._state = zone_check


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