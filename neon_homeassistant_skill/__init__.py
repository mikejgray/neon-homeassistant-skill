from mycroft_bus_client import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
from mycroft import intent_handler

__version__ = "0.0.1"

# https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant/blob/master/ovos_PHAL_plugin_homeassistant/__init__.py
class NeonHomeAssistantSkill(MycroftSkill):
    """Home Assistant skill for Neon OS. Requires the PHAL Home Assistant plugin."""

    def __init__(self):
        super(NeonHomeAssistantSkill, self).__init__(name="HomeAssistantSkill")

    @intent_handler("sensor.intent")
    def get_device_intent(self, message):
        """Handle intent to get a single device from Home Assistant."""
        bus_target = "ovos.phal.plugin.homeassistant.get.device"
        self._get_device_intent(bus_target, message.data)
        self.bus.emit(Message(bus_target, message.data))

    def _get_device_intent(self, event, data):
        """Handle intent to get a single device from Home Assistant."""
        LOG.debug(data)
        self.add_event(event, data)

    @intent_handler("turn.on.intent")
    def handle_turn_on_intent(self, message) -> None:
        """Handle turn on intent."""
        LOG.debug(message.data)
        self.add_event("ovos.phal.plugin.homeassistant.device.turn_on", message.data)

    @intent_handler("turn.off.intent")
    @intent_handler("stop.intent")
    def handle_turn_off_intent(self, message) -> None:
        """Handle turn off intent."""
        LOG.debug(message.data)
        self.add_event("ovos.phal.plugin.homeassistant.device.turn_on", message.data)

    # @intent_handler("call.supported.function.intent")
    # def handle_call_supported_function(self, message) -> None:
    #     """Handle call supported function intent."""
    #     LOG.debug(message.data)
    #     self.add_event("ovos.phal.plugin.homeassistant.call.supported.function", message.data)

    # Intent handlers from Mycroft  # TODO:

    # @intent_handler("show.camera.image.intent")
    # def handle_show_camera_image_intent(self, message) -> None:
    #     """Handle show camera image intent."""

    # @intent_handler("open.intent")
    # def handle_open(self, message) -> None:
    #     """Handle open intent."""

    # @intent_handler("close.intent")
    # def handle_close(self, message) -> None:
    #     """Handle close intent."""

    # @intent_handler("toggle.intent")
    # def handle_toggle_intent(self, message) -> None:
    #     """Handle toggle intent."""

    # @intent_handler("sensor.intent")
    # def handle_sensor_intent(self, message) -> None:
    #     """Handle sensor intent."""

    # @intent_handler("set.light.brightness.intent")
    # def handle_light_set_intent(self, message) -> None:
    #     """Handle set light brightness intent."""

    # @intent_handler("increase.light.brightness.intent")
    # def handle_light_increase_intent(self, message) -> None:
    #     """Handle increase light brightness intent."""

    # @intent_handler("decrease.light.brightness.intent")
    # def handle_light_decrease_intent(self, message) -> None:
    #     """Handle decrease light brightness intent."""

    # @intent_handler("automation.intent")
    # def handle_automation_intent(self, message) -> None:
    #     """Handle automation intent."""

    # @intent_handler("tracker.intent")
    # def handle_tracker_intent(self, message) -> None:
    #     """Handle tracker intent."""

    # @intent_handler("set.climate.intent")
    # def handle_set_thermostat_intent(self, message) -> None:
    #     """Handle set climate intent."""

    # @intent_handler("add.item.shopping.list.intent")
    # def handle_shopping_list_intent(self, message) -> None:
    #     """Handle add item to shopping list intent."""

    # def _handle_camera_image_actions(self, message) -> None:
    #     """Handler for camera image actions."""

    # def _handle_turn_actions(self, message) -> None:
    #     """Handler for turn on/off and toggle actions."""

    # def _handle_light_set(self, message) -> None:
    #     """Handle set light action."""

    # def _handle_shopping_list(self, message) -> None:
    #     """Handler for add item to shopping list action."""

    # def _handle_open_close_actions(self, message) -> None:
    #     """Handler for open and close actions."""

    # def _handle_light_adjust(self, message) -> None:
    #     """Handler for light brightness increase and decrease action"""

    # def _handle_automation(self, message) -> None:
    #     """Handler for triggering automations."""

    # def _dialog_sensor_climate(self, name: str, state: str, attr: dict) -> None:
    #     """Handle dialogs for sensor climate."""

    # def _handle_sensor(self, message) -> None:
    #     """Handler sensors reading"""
    #     # IDEA: Add some context if the person wants to look the unit up
    #     # Maybe also change to name
    #     # if one wants to look up "outside temperature"
    #     # self.set_context("SubjectOfInterest", sensor_unit)

    # def _handle_set_thermostat(self, message) -> None:
    #     pass

    # def _display_sensor_dialog(self, name, value, description=""):
    #     pass

    # def handle_fallback(self, message) -> bool:
    #     """
    #     Handler for direct fallback to Home Assistants
    #     conversation module.

    #     Returns:
    #         True/False state of fallback registration
    #     """
    #     return True


def create_skill():
    return NeonHomeAssistantSkill()
