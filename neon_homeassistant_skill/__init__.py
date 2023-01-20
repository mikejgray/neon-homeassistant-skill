from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
from mycroft import intent_handler

__version__ = "0.1.0"

class HomeAssistantSkill(MycroftSkill):
    def __init__(self):
        super(HomeAssistantSkill, self).__init__(name="HomeAssistantSkill")

    def _setup(self):
        pass

    def _force_setup(self):
        pass

    def _register_tracker_entities(self) -> None:
        """List tracker entities.

        Add them to entity file and registry it so
        Padatious react only to known entities.
        Should fix conflict with Where is skill.
        """
        pass

    def on_websettings_changed(self) -> None:
        """
        Force a setting refresh after the websettings changed
        otherwise new settings will not be regarded.
        """
        pass

    def _find_entity(self):
        pass

    def _check_availability(self):
        pass

        # Intent handlers

    @intent_handler("show.camera.image.intent")
    def handle_show_camera_image_intent(self, message) -> None:
        """Handle show camera image intent."""
        pass

    @intent_handler("turn.on.intent")
    def handle_turn_on_intent(self, message) -> None:
        """Handle turn on intent."""
        pass

    @intent_handler("turn.off.intent")
    def handle_turn_off_intent(self, message) -> None:
        """Handle turn off intent."""
        pass

    @intent_handler("open.intent")
    def handle_open(self, message) -> None:
        """Handle open intent."""
        pass

    @intent_handler("close.intent")
    def handle_close(self, message) -> None:
        """Handle close intent."""
        pass

    @intent_handler("stop.intent")
    def handle_stop(self, message) -> None:
        """Handle stop intent."""
        pass

    @intent_handler("toggle.intent")
    def handle_toggle_intent(self, message) -> None:
        """Handle toggle intent."""
        pass

    @intent_handler("sensor.intent")
    def handle_sensor_intent(self, message) -> None:
        """Handle sensor intent."""
        pass

    @intent_handler("set.light.brightness.intent")
    def handle_light_set_intent(self, message) -> None:
        """Handle set light brightness intent."""
        pass

    @intent_handler("increase.light.brightness.intent")
    def handle_light_increase_intent(self, message) -> None:
        """Handle increase light brightness intent."""
        pass

    @intent_handler("decrease.light.brightness.intent")
    def handle_light_decrease_intent(self, message) -> None:
        """Handle decrease light brightness intent."""
        pass

    @intent_handler("automation.intent")
    def handle_automation_intent(self, message) -> None:
        """Handle automation intent."""
        pass

    @intent_handler("tracker.intent")
    def handle_tracker_intent(self, message) -> None:
        """Handle tracker intent."""
        pass

    @intent_handler("set.climate.intent")
    def handle_set_thermostat_intent(self, message) -> None:
        """Handle set climate intent."""
        pass

    @intent_handler("add.item.shopping.list.intent")
    def handle_shopping_list_intent(self, message) -> None:
        """Handle add item to shopping list intent."""
        pass

    def _handle_camera_image_actions(self, message) -> None:
        """Handler for camera image actions."""
        pass

    def _handle_turn_actions(self, message) -> None:
        """Handler for turn on/off and toggle actions."""
        pass

    def _handle_light_set(self, message) -> None:
        """Handle set light action."""
        pass

    def _handle_shopping_list(self, message) -> None:
        """Handler for add item to shopping list action."""
        pass

    def _handle_open_close_actions(self, message) -> None:
        """Handler for open and close actions."""
        pass

    def _handle_stop_actions(self, message):
        """Handler for stop actions."""
        pass

    def _handle_light_adjust(self, message) -> None:
        """Handler for light brightness increase and decrease action"""
        pass

    def _handle_automation(self, message) -> None:
        """Handler for triggering automations."""
        pass

    def _dialog_sensor_climate(self, name: str, state: str, attr: dict) -> None:
        """Handle dialogs for sensor climate."""
        pass

    def _handle_sensor(self, message) -> None:
        """Handler sensors reading"""
        pass
        # IDEA: Add some context if the person wants to look the unit up
        # Maybe also change to name
        # if one wants to look up "outside temperature"
        # self.set_context("SubjectOfInterest", sensor_unit)

    # In progress, still testing.
    # Device location works.
    # Proximity might be an issue
    # - overlapping command for directions modules
    # - (e.g. "How far is x from y?")
    def _handle_tracker(self, message) -> None:
        """Handler for finding trackers position."""
        pass

    def _handle_set_thermostat(self, message) -> None:
        pass

    def _display_sensor_dialog(self, name, value, description=""):
        pass

    def handle_fallback(self, message) -> bool:
        """
        Handler for direct fallback to Home Assistants
        conversation module.

        Returns:
            True/False state of fallback registration
        """
        pass

    def initialize(self):
        """Initialize skill, set language and priority."""
        get_devices_intent = (
            IntentBuilder("get_devices_intent").require("GetDevicesKeyword").require("HomeAssistantKeyword").build()
        )
        get_device_intent = (
            IntentBuilder("get_device_intent").require("GetDeviceKeyword").require("HomeAssistantKeyword").build()
        )
        handle_turn_on_intent = (
            IntentBuilder("handle_turn_on_intent").require("TurnOnKeyword").require("HomeAssistantKeyword").build()
        )
        handle_turn_off_intent = (
            IntentBuilder("handle_turn_off_intent").require("TurnOffKeyword").require("HomeAssistantKeyword").build()
        )
        self.register_intent(get_devices_intent, self.get_devices_intent)
        self.register_intent(get_device_intent, self.get_device_intent)
        self.register_intent(handle_turn_on_intent, self.handle_turn_on_intent)
        self.register_intent(handle_turn_off_intent, self.handle_turn_off_intent)

    def get_devices_intent(self, message):
        LOG.debug(message.data)
        self.speak("Getting a list of devices from Home Assistant.")

    def get_device_intent(self, message):
        LOG.debug(message.data)
        self.speak(f"Getting device {message.data} from Home Assistant.")

    def handle_turn_on_intent(self, message):
        LOG.debug(message.data)
        self.speak(f"Turning on {message.data}")

    def handle_turn_off_intent(self, message):
        LOG.debug(message.data)
        self.speak(f"Turning off {message.data}")

    def stop(self):
        pass


def create_skill():
    return HomeAssistantSkill()
