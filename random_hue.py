import asyncio
import logging
import random

import voluptuous as vol

from homeassistant.components.scene import Scene
from homeassistant.const import CONF_PLATFORM, CONF_NAME, ATTR_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.components.light import (is_on, ATTR_BRIGHTNESS, ATTR_TRANSITION, ATTR_WHITE_VALUE, ATTR_HS_COLOR, DOMAIN as LIGHT_DOMAIN)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_LIGHTS = 'lights'
CONF_TRANSITION = 'transition'
CONF_SAME_COLOR = 'same_color'

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_PLATFORM): 'random_hue',
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_LIGHTS): cv.entity_ids,
    vol.Optional(CONF_TRANSITION): cv.positive_int,
    vol.Optional(CONF_SAME_COLOR): cv.boolean,
})

# pylint: disable=unused-argument
@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    name = config.get(CONF_NAME, "Random Color")
    lights = config.get(CONF_LIGHTS)
    transition = config.get(CONF_TRANSITION, 0)
    same_color = config.get(CONF_SAME_COLOR, False)

    scene = RandomHue(hass, name, lights, transition, same_color)
    async_add_devices([scene])
    return True

class RandomHue(Scene):
    def __init__(self, hass, name, lights, transition, same_color):
        self.hass = hass
        self._name = name
        self._lights = lights
        self._transition = transition
        self._same_color = same_color

    @property
    def name(self):
        return self._name

    def activate(self):
        hs = None

        for entity in self._lights:
            if not is_on(self.hass, entity):
                return

            if hs is None or not self._same_color:
                hs = [ random.random() * 360, 100 ]

            _LOGGER.debug("Setting light %s to %s", entity, hs)

            service_data = {
                ATTR_ENTITY_ID: entity,
                ATTR_HS_COLOR: hs,
                ATTR_WHITE_VALUE: 0,
                ATTR_TRANSITION: self._transition,
            }

            self.hass.services.call(LIGHT_DOMAIN, SERVICE_TURN_ON, service_data)
