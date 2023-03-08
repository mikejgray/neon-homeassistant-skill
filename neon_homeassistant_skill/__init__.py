import asyncio

from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from pfzy import fuzzy_match

__version__ = "0.0.8"


# https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant/blob/master/ovos_PHAL_plugin_homeassistant/__init__.py
class NeonHomeAssistantSkill(MycroftSkill):
    """Home Assistant skill for Neon OS. Requires the PHAL Home Assistant plugin."""

    def __init__(self):
        super(NeonHomeAssistantSkill, self).__init__(name="NeonHomeAssistantSkill")
        self.devices_list = None
        self.skill_id = "neon-homeassistant-skill"

    def initialize(self):
        self._build_device_list()
        self.bus.on("ovos.phal.plugin.homeassistant.get.devices.response", self._handle_device_list)
        self.bus.on("ovos.phal.plugin.homeassistant.device.state.updated", self._handle_device_state_update)
        # TODO: Try to get a response from the PHAL skill. If no response, ask user if they want to load it
        # Keep state in settings

    def _build_device_list(self):
        self.bus.emit(Message("ovos.phal.plugin.homeassistant.get.devices", None, {"skill_id": self.skill_id}))

    def _handle_device_list(self, message):
        self.devices_list = message.data

    def _handle_device_state_update(self, _):
        self._build_device_list()

    @intent_handler("sensor.intent")
    def get_device_intent(self, message):
        """Handle intent to get a single device from Home Assistant."""
        LOG.info(message.data)
        device, device_id = self._get_device_from_message(message)
        if device and device_id:
            dev = self._get_device_info(device_id)
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.show.device.dashboard",
                    {"device_id": device_id, "device_type": dev.get("type")},
                )
            )
            self.speak_dialog(
                "device.status", data={"device": device, "type": dev.get("type"), "state": dev.get("state")}
            )
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("turn.on.intent")
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
    def handle_turn_off_intent(self, message) -> None:
        """Handle turn off intent."""
        LOG.info(message.data)
        device, device_id = self._get_device_from_message(message)
        if device and device_id:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.device.turn_off", {"device_id": device_id}))
            self.speak_dialog("device.turned.off", data={"device": device})
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("open.dashboard.intent")
    def handle_open_dashboard_intent(self, _):
        self.bus.emit(Message("ovos-PHAL-plugin-homeassistant.home"))
        self.speak_dialog("ha.dashboard.opened")

    @intent_handler("close.dashboard.intent")
    def handle_close_dashboard_intent(self, _):
        self.bus.emit(Message("ovos-PHAL-plugin-homeassistant.close"))
        self.speak_dialog("ha.dashboard.closed")

    @intent_handler("lights.get.brightness.intent")
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

    @intent_handler("lights.set.brightness.intent")
    def handle_set_brightness_intent(self, message: Message):
        device, device_id = self._get_device_from_message(message)
        if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
            brightness = message.data.get("brightness")
            call_data = {
                "device_id": device_id,
                "function_name": "turn_on",
                "function_args": {"brightness": self._get_ha_value_from_percentage_brightness(brightness)},
            }
            LOG.info(call_data)
            self.bus.emit(
                Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data, message.context)
            )
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("device.not.found", data={"device": device})

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
        color = self._get_device_info(device_id).get("attributes", {}).get("rgb_color")
        LOG.info(device)
        LOG.info(device_id)
        if device_id:
            for dev in self.devices_list:
                if dev["id"] == device_id:
                    color = dev["attributes"].get("rgb_color")
                    LOG.info(dev)
                    if color:
                        self.speak_dialog("lights.current.color", data={"color": color, "device": device})
                    else:
                        self.speak_dialog("lights.status.not.available", data={"device": device, "status": "color"})

    @intent_handler("lights.set.color.intent")
    def handle_set_color_intent(self, message):
        device, device_id = self._get_device_from_message(message)
        if device and device_id:
            dev = self._get_device_info(device_id)
            brightness = dev.get("attributes", {}).get("brightness")

            call_data = {
                "device_id": device_id,
                "function_name": "turn_on",
                "data": {"brightness": brightness, "rgb_color": message.data.get("color")},
            }
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("show.area.dashboard.intent")
    def handle_show_area_dashboard_intent(self, message):
        area = message.get("area")
        if area:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.show.area.dashboard"), {"area": area})
            self.speak_dialog("area.dashboard.opened", data={"area": area})
        else:
            self.speak_dialog("area.not.found")

    # @intent_handler("vacuum.action.intent")  # TODO: Find an intent that doesn't conflict with OCP
    # def handle_vacuum_action_intent(self, message):
    #     device, device_id = self._get_device_from_message(message)
    #     if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
    #         dev = self._get_device_info(device_id)
    #         action = message.data.get("action")
    #         if action in ("start", "stop", "pause"):
    #             if dev.get("type") == "vacuum":
    #                 call_data = {
    #                     "device_id": device_id,
    #                     "function_name": message.data.get("action"),
    #                 }
    #                 LOG.info(call_data)
    #                 self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
    #             self.speak_dialog("acknowledge")
    #         else:
    #             self.speak("vacuum.action.not.found", data={"action": action})
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    # Internal helpers
    def _fuzzy_match_name(self, spoken_name, device_names):
        result = asyncio.run(fuzzy_match(spoken_name, device_names))
        if result:
            return self.devices_list[device_names.index(result[0])]["id"]
        else:
            return None

    def _get_device_from_message(self, message):
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


def create_skill():
    return NeonHomeAssistantSkill()
