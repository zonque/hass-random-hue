import asyncio
import logging
import random

import voluptuous as vol

from homeassistant.components.scene import Scene
from homeassistant.const import CONF_PLATFORM, CONF_NAME
import homeassistant.helpers.config_validation as cv
import homeassistant.components.light as light

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

    @asyncio.coroutine
    def async_activate(self):
        hs = None

        for entity in self._lights:
            if not light.is_on(self.hass, entity):
                return

            if hs is None or not self._same_color:
                hs = [ random.random() * 360, 100 ]

            logging.debug("Setting light %s to %s", entity, hs)
            light.turn_on(self.hass, entity_id=entity, hs_color=hs, white_value=0, transition=self._transition)
