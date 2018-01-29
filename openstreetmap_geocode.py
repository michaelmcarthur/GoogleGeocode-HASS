"""
Support for Open Street Map Geocode sensors.

For more details about this platform, please refer to the documentation at
https://github.com/michaelmcarthur/GoogleGeocode-HASS
"""
# from datetime import datetime
from datetime import timedelta
import json
import logging
# import requests
from requests import get

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_API_KEY, CONF_NAME, CONF_SCAN_INTERVAL, ATTR_ATTRIBUTION,
    ATTR_LATITUDE, ATTR_LONGITUDE)
import homeassistant.helpers.location as location
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_ORIGIN = 'origin'
CONF_OPTIONS = 'options'
CONF_DISPLAY_ZONE = 'display_zone'
CONF_ATTRIBUTION = "Data provided by OpenStreetMap"
CONF_GRAVATAR = 'gravatar'

ATTR_PLACE = 'Place'
ATTR_STREET_NUMBER = "Street Number"
ATTR_STREET = 'Street'
ATTR_CITY = 'City'
ATTR_POSTAL_TOWN = "Postal Town"
ATTR_POSTAL_CODE = "Postal Code"
ATTR_REGION = 'State'
ATTR_COUNTRY = 'Country'
ATTR_COUNTY = 'County'
ATTR_FORMATTED_ADDRESS = "Formatted Address"

DEFAULT_NAME = 'OpenStreetMap Geocode'
DEFAULT_OPTION = "street, city"
DEFAULT_DISPLAY_ZONE = 'display'
DEFAULT_KEY = "no key"
CURRENT = "0,0"
ZONE_CHECK = 'a'
#'''change this for testing'''
SCAN_INTERVAL = timedelta(seconds=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ORIGIN): cv.string,
    vol.Optional(CONF_API_KEY, default=DEFAULT_KEY): cv.string,
    vol.Optional(CONF_OPTIONS, default=DEFAULT_OPTION): cv.string,
    vol.Optional(CONF_DISPLAY_ZONE, default=DEFAULT_DISPLAY_ZONE): cv.string,
    vol.Optional(CONF_GRAVATAR, default=None): vol.Any(None, cv.string),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL):
        cv.time_period,
})

TRACKABLE_DOMAINS = ['device_tracker', 'sensor']


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    name = config.get(CONF_NAME)
    api_key = config.get(CONF_API_KEY)
    origin = config.get(CONF_ORIGIN)
    options = config.get(CONF_OPTIONS)
    display_zone = config.get(CONF_DISPLAY_ZONE)
    gravatar = config.get(CONF_GRAVATAR)

    add_devices([GoogleGeocode(hass, origin, name, api_key, options,
                               display_zone, gravatar)])


class GoogleGeocode(Entity):
    """Representation of a Google Geocode Sensor."""

    def __init__(self, hass, origin, name, api_key, options, display_zone,
                 gravatar):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._api_key = api_key
        self._options = options.lower()
        self._display_zone = display_zone.lower()
        self._state = "Awaiting Update"
        self._gravatar = gravatar

        self._street_number = None
        self._street = None
        self._city = None
        self._postal_town = None
        self._postal_code = None
        self._city = None
        self._region = None
        self._country = None
        self._county = None
        self._place = None
        self._formatted_address = None
        self._zone_check_current = None

        # Check if origin is a trackable entity
        if origin.split('.', 1)[0] in TRACKABLE_DOMAINS:
            self._origin_entity_id = origin
        else:
            self._origin = origin

        if gravatar is not None:
            self._picture = self._get_gravatar_for_email(gravatar)
        else:
            self._picture = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def entity_picture(self):
        """Return the picture of the device."""
        return self._picture

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return{
            ATTR_STREET_NUMBER: self._street_number,
            ATTR_STREET: self._street,
            ATTR_CITY: self._city,
            ATTR_POSTAL_TOWN: self._postal_town,
            ATTR_POSTAL_CODE: self._postal_code,
            ATTR_REGION: self._region,
            ATTR_COUNTRY: self._country,
            ATTR_COUNTY: self._county,
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
            ATTR_PLACE: self._place,
            ATTR_FORMATTED_ADDRESS: self._formatted_address,
        }

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Get the latest data and updates the states."""

        if hasattr(self, '_origin_entity_id'):
            self._origin = self._get_location_from_entity(
                self._origin_entity_id
            )

        global CURRENT
        global zone_check_count
        global ZONE_CHECK
        global user_display
        ZONE_CHECK = self.hass.states.get(self._origin_entity_id).state
        zone_check_count = 2

        if ZONE_CHECK == self._zone_check_current:
            zone_check_count = 1
        if ZONE_CHECK == 'not_home':
            zone_check_count = 2
        if zone_check_count == 1:
            pass
        elif self._origin is None:
            pass
        elif CURRENT == self._origin:
            pass
        else:
            _LOGGER.info("google request sent")
            self._zone_check_current = (
                self.hass.states.get(self._origin_entity_id).state)
            zone_check_count = 2
            lat = self._origin
            CURRENT = lat
            self._reset_attributes()
#remove else
            if self._api_key == "no key":
                url = "http://nominatim.openstreetmap.org/reverse?format=json&lat=" + lat + "&zoom=18&addressdetails=1&namedetails=1"
            else:
                url = ('https://maps.googleapis.com/maps/api/geocode/json?'+(
                    'latlng=' + lat + '&key=' + self._api_key))
            response = get(url)
            json_input = response.text
            decoded = json.loads(json_input)
            street_number = ''
            street = "Unnamed Road"
            alt_street = "Unnamed Road"
            city = ''
            place = ''
            postal_town = ''
            formatted_address = ''
            state = ''
            county = ''
            country = ''

#all changed just need to figure out the for result in part'''
            for result in decoded:
                if 'house_number' in decoded["address"]:
                    street_number = decoded["address"]["house_number"]
                    self._street_number = street_number
                if 'road' in decoded["address"]:
                    street = decoded["address"]["road"]
                    self._street = street
                if 'town' in decoded["address"]:
                    postal_town = decoded["address"]["town"]
                    self._postal_town = postal_town
                if 'city' in decoded["address"]:
                    city = decoded["address"]["city"]
                    self._city = city
                if 'state' in decoded["address"]:
                    state = decoded["address"]["state"]
                    self._region = state
                if 'county' in decoded["address"]:
                    county = decoded["address"]["county"]
                    self._county = county
                if 'country' in decoded["address"]:
                    country = decoded["address"]["country"]
                    self._country = country
                if 'postcode' in decoded["address"]:
                    postal_code = decoded["address"]["postcode"]
                    self._postal_code = postal_code
                if "name" in decoded["namedetails"]:
                    place = decoded["namedetails"]["name"]
                    self._place = place
            try:
                if 'display_name' in decoded:
                    formatted_address = (
                        decoded["display_name"])
                    self._formatted_address = formatted_address
            except IndexError:
                pass

#'''error message wont be correct'''
            if 'error_message' in decoded:
                self._state = decoded['error_message']
                _LOGGER.error("You have exceeded your daily requests or "(
                    "entered a incorrect key please create or check the"
                    "api key."))
#'''this might not work check what unnamed road is in osm'''
            elif self._display_zone == 'hide' or ZONE_CHECK == "not_home":
                if street == '':
                    street = alt_street
                    self._street = alt_street
                if city == '':
                    city = postal_town
                    if city == '':
                        city = county

                display_options = self._options
                user_display = []

                if "place" in display_options:
                    user_display.append(place)
                if "street_number" in display_options:
                    user_display.append(street_number)
                if "street" in display_options:
                    user_display.append(street)
                if "city" in display_options:
                    self._append_to_user_display(city)
                if "county" in display_options:
                    self._append_to_user_display(county)
                if "state" in display_options:
                    self._append_to_user_display(state)
                if "postal_code" in display_options:
                    self._append_to_user_display(postal_code)
                if "country" in display_options:
                    self._append_to_user_display(country)
                if "formatted_address" in display_options:
                    self._append_to_user_display(formatted_address)

                user_display = ', '.join(x for x in user_display)

                if user_display == '':
                    user_display = street
                self._state = user_display
            else:
                self._state = ZONE_CHECK[0].upper() + ZONE_CHECK[1:]
                self._reset_attributes()

    def _get_location_from_entity(self, entity_id):
        """Get the origin from the entity state or attributes."""
        entity = self._hass.states.get(entity_id)

        if entity is None:
            _LOGGER.error("Unable to find entity %s", entity_id)
            return None

        # Check if the entity has origin attributes
        if location.has_location(entity):
            return self._get_location_from_attributes(entity)

        # When everything fails just return nothing
        return None

    def _reset_attributes(self):
        """Resets attributes."""
        self._street = None
        self._street_number = None
        self._city = None
        self._postal_town = None
        self._postal_code = None
        self._region = None
        self._country = None
        self._county = None
        self._formatted_address = None
        self._place = None

    def _append_to_user_display(self, append_check):
        """Appends attribute to state if false."""
        if append_check == '':
            pass
        else:
            user_display.append(append_check)

    @staticmethod
    def _get_location_from_attributes(entity):
        """Get the lat/long string from an entities attributes."""
        attr = entity.attributes
        return "%s&lon=%s" % (attr.get(ATTR_LATITUDE), attr.get(ATTR_LONGITUDE))

    def _get_gravatar_for_email(self, email: str):
        """Return an 80px Gravatar for the given email address.
        Async friendly.
        """
        import hashlib
        url = 'https://www.gravatar.com/avatar/{}.jpg?s=80&d=wavatar'
        return url.format(
            (hashlib.md5(email.encode('utf-8').lower()).hexdigest()))
