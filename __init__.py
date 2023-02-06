import asyncio

from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from pfzy import fuzzy_match

__version__ = "0.0.6"


# https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant/blob/master/ovos_PHAL_plugin_homeassistant/__init__.py
class NeonHomeAssistantSkill(MycroftSkill):
    """Home Assistant skill for Neon OS. Requires the PHAL Home Assistant plugin."""

    def __init__(self):
        super(NeonHomeAssistantSkill, self).__init__(name="NeonHomeAssistantSkill")
        self.devices_list = None

    def initialize(self):
        self._build_device_list()
        self.bus.on("ovos.phal.plugin.homeassistant.get.devices.response", self._handle_device_list)
        self.bus.on("ovos.phal.plugin.homeassistant.device.state.updated", self._handle_device_state_update)

    def _build_device_list(self):
        self.bus.emit(Message("ovos.phal.plugin.homeassistant.get.devices"))

    def _handle_device_list(self, message):
        self.devices_list = message.data

    def _handle_device_state_update(self, message):
        self._build_device_list()

    @intent_handler("sensor.intent")  # Tested live, no GUI
    def get_device_intent(self, message):
        """Handle intent to get a single device from Home Assistant."""
        LOG.info(message.data)
        device, device_id = self._get_device_from_message(message)
        if device and device_id:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.get.device", {"device_id": device_id}))
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("turn.on.intent")  # Tested live
    def handle_turn_on_intent(self, message) -> None:
        """Handle turn on intent."""
        LOG.info(message.data)
        device, device_id = self._get_device_from_message(message)
        if device and device_id:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.device.turn_on", {"device_id": device_id}))
            self.speak_dialog("device.turned.on", data={"device": device})
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("turn.off.intent")
    @intent_handler("stop.intent")
    def handle_turn_off_intent(self, message) -> None:  # Tested live
        """Handle turn off intent."""
        LOG.info(message.data)
        device, device_id = self._get_device_from_message(message)
        if device and device_id:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.device.turn_off", {"device_id": device_id}))
            self.speak_dialog("device.turned.off", data={"device": device})
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("open.dashboard.intent")  # Tested live, no GUI
    def handle_open_dashboard_intent(self, message):
        self.bus.emit(Message("ovos-PHAL-plugin-homeassistant.home"))
        self.speak_dialog("ha.dashboard.opened")

    @intent_handler("close.dashboard.intent")  # Tested live, no GUI
    def handle_close_dashboard_intent(self, message):
        self.bus.emit(Message("ovos-PHAL-plugin-homeassistant.close"))
        self.speak_dialog("ha.dashboard.closed")

    @intent_handler("lights.get.brightness.intent")  # Tested, but inconsistent...it's not always finding devices well
    def handle_get_brightness_intent(self, message):
        LOG.info(message.data)
        device, device_id = self._get_device_from_message(message)
        if device and device_id:
            brightness = self._get_device_info(device_id).get("attributes", {}).get("brightness")
            LOG.info(brightness)
            if brightness:
                self.speak_dialog(
                    "lights.current.brightness",
                    data={
                        "brightness": self._get_percentage_brightness_from_ha_value(brightness),
                        "device": device,
                    },
                )
            else:
                self.speak_dialog("lights.status.not.available", data={"device": device})
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("lights.set.brightness.intent")  # Tested live, no GUI
    def handle_set_brightness_intent(self, message):
        device, device_id = self._get_device_from_message(message)
        if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
            brightness = message.data.get("brightness")
            call_data = {
                "device_id": device_id,
                "function_name": "turn_on",
                "function_args": {"brightness": self._get_ha_value_from_percentage_brightness(brightness)},
            }
            LOG.info(call_data)
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    # Tested live, no GUI. Works once then status isn't being updated from PHAL.
    @intent_handler("lights.increase.brightness.intent")
    def handle_increase_brightness_intent(self, message):
        device, device_id = self._get_device_from_message(message)
        if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
            brightness = self._get_device_info(device_id).get("attributes", {}).get("brightness")
            if brightness:
                increased_percentage = min(self._get_percentage_brightness_from_ha_value(brightness) + 10, 100)
                call_data = {
                    "device_id": device_id,
                    "function_name": "turn_on",
                    "function_args": {
                        "brightness": self._get_ha_value_from_percentage_brightness(increased_percentage)
                    },
                }
                self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
                self.speak_dialog("acknowledge")
            else:
                self.speak_dialog("lights.status.not.available", data={"device": device})
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    # Tested live, no GUI. Works once then status isn't being updated from PHAL.
    @intent_handler("lights.decrease.brightness.intent")
    def handle_decrease_brightness_intent(self, message):
        device, device_id = self._get_device_from_message(message)
        if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
            brightness = self._get_device_info(device_id).get("attributes", {}).get("brightness")
            if brightness:
                decreased_percentage = max(self._get_percentage_brightness_from_ha_value(brightness) - 10, 0)
                call_data = {
                    "device_id": device_id,
                    "function_name": "turn_on",
                    "function_args": {
                        "brightness": self._get_ha_value_from_percentage_brightness(decreased_percentage)
                    },
                }
                self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
                self.speak_dialog("acknowledge")
            else:
                self.speak_dialog("lights.status.not.available", data={"device": device})
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("lights.get.color.intent")
    def handle_get_color_intent(self, message):
        device, device_id = self._get_device_from_message(message)
        if device_id:
            for dev in self.devices_list:
                if dev["id"] == device_id:
                    color = dev["attributes"].get("rgb_color")
                    if color:
                        self.speak_dialog("lights.current.color", data={"color": color, "device": device})
                    else:
                        self.speak_dialog("lights.status.not.available", data={"device": device, "status": "color"})

    @intent_handler("lights.set.color.intent")
    def handle_set_color_intent(self, message):
        device, device_id = self._get_device_from_message(message)
        device_id = self._get_device_id(device)
        if device_id:
            for device in self.devices_list:
                if device["id"] == device_id:
                    brightness = device["attributes"].get("brightness")
                    break

            call_data = {
                "device_id": device_id,
                "function_name": "turn_on",
                "data": {"brightness": brightness, "rgb_color": message.data.get("color")},
            }
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    def _fuzzy_match_name(self, spoken_name, device_names):
        result = asyncio.run(fuzzy_match(spoken_name, device_names))
        if result:
            return self.devices_list[device_names.index(result[0])]["id"]
        else:
            return None

    def _get_device_from_message(self, message):  # Tested live
        device = message.data.get("entity", "")
        LOG.info(f"Device: {device}")
        device_id = self._get_device_id(device)
        LOG.info(f"Device ID: {device_id}")
        return device, device_id

    def _get_device_id(self, spoken_name):
        device_names = []

        if not self.devices_list:
            return None

        for device in self.devices_list:
            if device["attributes"].get("friendly_name"):
                device_names.append(device["attributes"]["friendly_name"].lower())
            else:
                device_names.append(device["name"].lower())
        LOG.debug(device_names)
        spoken_name = spoken_name.lower()
        if spoken_name in device_names:
            return self.devices_list[device_names.index(spoken_name)]["id"]
        else:
            fuzzy_result = self._fuzzy_match_name(spoken_name, device_names)
            return fuzzy_result if fuzzy_result else None

    def _get_device_info(self, device_id):
        return [x for x in self.devices_list if x["id"] == device_id][0]

    def _get_percentage_brightness_from_ha_value(self, brightness):
        return round(int(brightness) / 255 * 100)

    def _get_ha_value_from_percentage_brightness(self, brightness):
        return round(int(brightness)) / 100 * 255

    def _search_for_device_by_id(self, device_id):
        """Returns index of device or None if not found."""
        for i, dic in enumerate(self.devices_list):
            if dic["id"] == device_id:
                return i
        return None

    # Supported bus events in OVOS PHAL plugin
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.get.device.display.model"))
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.get.device.display.list.model"))
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.start.oauth.flow"))
    # # GUI EVENTS
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.show.device.dashboard"))
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.show.area.dashboard"))
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.update.device.dashboard"))
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.update.area.dashboard"))
    # self.bus.emit(Message("ovos.phal.plugin.homeassistant.set.group.display.settings"))

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
