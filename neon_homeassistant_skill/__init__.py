# pylint: disable=missing-function-docstring,missing-class-docstring,missing-module-docstring
from typing import List

from ovos_bus_client import Message
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


def chunks(lst, n_len) -> List[list]:
    """Split list into n-length chunks."""
    n_len = max(1, n_len)
    return [lst[i : i + n_len] for i in range(0, len(lst), n_len)]


# https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant/blob/master/ovos_PHAL_plugin_homeassistant/__init__.py
class NeonHomeAssistantSkill(OVOSSkill):
    """Home Assistant skill for Neon OS. Requires the PHAL Home Assistant plugin."""

    def __init__(self, *args, **kwargs):
        super(NeonHomeAssistantSkill, self).__init__(*args, **kwargs)
        self.skill_id = "neon-homeassistant-skill"

    def initialize(self):
        self.bus.on("ovos.phal.plugin.homeassistant.assist.message.response", self._handle_assist_error)
        self.bus.on("ovos.phal.plugin.homeassistant.get.device.response", self.handle_get_device_response)
        self.bus.on("ovos.phal.plugin.homeassistant.device.turn_on.response", self.handle_turn_on_response)
        self.bus.on("ovos.phal.plugin.homeassistant.device.turn_off.response", self.handle_turn_off_response)

    # Handlers
    @intent_handler("sensor.intent")
    def get_device_intent(self, message):
        """Handle intent to get a single device status from Home Assistant."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.get.device",
                    {"device": device},
                )
            )
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_get_device_response(self, message):
        self.log.info(message.data)
        device = message.data
        if device:
            self.speak_dialog(
                "device.status",
                data={
                    "device": device.get("attributes", {}).get("friendly_name", device.get("name")),
                    "type": device.get("type"),
                    "state": device.get("state"),
                },
            )
        else:
            self.speak_dialog("device.not.found")

    @intent_handler("turn.on.intent")
    def handle_turn_on_intent(self, message) -> None:
        """Handle turn on intent."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.device.turn_on", {"device": device}))
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_turn_on_response(self, message) -> None:
        """Handle turn on intent response."""
        self.log.debug(f"Handling turn on response to {message.data}")
        device = message.data.get("device", "")
        if device:
            self.speak_dialog("device.turned.on", data={"device": device})
        else:
            self.speak_dialog("no.parsed.device")

    @intent_handler("turn.off.intent")
    @intent_handler("stop.intent")  # Consider changing this so it stops reading from the list of devices
    def handle_turn_off_intent(self, message) -> None:
        """Handle turn off intent."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.device.turn_off", {"device": device}))
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_turn_off_response(self, message) -> None:
        self.log.debug(f"Handling turn off response to {message.data}")
        device = message.data.get("device", "")
        if device:
            self.speak_dialog("device.turned.off", data={"device": device})
        else:
            self.speak_dialog("no.parsed.device")

    @intent_handler("open.dashboard.intent")
    def handle_open_dashboard_intent(self, _):
        self.bus.emit(Message("ovos-PHAL-plugin-homeassistant.home"))
        self.speak_dialog("ha.dashboard.opened")

    @intent_handler("close.dashboard.intent")
    def handle_close_dashboard_intent(self, _):
        self.bus.emit(Message("ovos-PHAL-plugin-homeassistant.close"))
        self.speak_dialog("ha.dashboard.closed")

    # @intent_handler("lights.get.brightness.intent")
    # def handle_get_brightness_intent(self, message):
    #     LOG.info(message.data)
    #     device, device_id = self._get_device_from_message(message)
    #     if device and device_id:
    #         brightness = self._get_device_info(device_id).get("attributes", {}).get("brightness")
    #         LOG.info(brightness)
    #         if brightness:
    #             self.speak_dialog(
    #                 "lights.current.brightness",
    #                 data={
    #                     "brightness": self._get_percentage_brightness_from_ha_value(brightness),
    #                     "device": device,
    #                 },
    #             )
    #         else:
    #             self.speak_dialog("lights.status.not.available", data={"device": device})
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    # @intent_handler("lights.set.brightness.intent")
    # def handle_set_brightness_intent(self, message: Message):
    #     device, device_id = self._get_device_from_message(message)
    #     if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
    #         brightness = message.data.get("brightness")
    #         call_data = {
    #             "device_id": device_id,
    #             "function_name": "turn_on",
    #             "function_args": {"brightness": self._get_ha_value_from_percentage_brightness(brightness)},
    #         }
    #         LOG.info(call_data)
    #         self.bus.emit(
    #             Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data, message.context)
    #         )
    #         self.speak_dialog("acknowledge")
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    # @intent_handler("lights.increase.brightness.intent")
    # def handle_increase_brightness_intent(self, message):
    #     device, device_id = self._get_device_from_message(message)
    #     if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
    #         brightness = self._get_device_info(device_id).get("attributes", {}).get("brightness")
    #         if brightness:
    #             increased_percentage = min(self._get_percentage_brightness_from_ha_value(brightness) + 10, 100)
    #             call_data = {
    #                 "device_id": device_id,
    #                 "function_name": "turn_on",
    #                 "function_args": {
    #                     "brightness": self._get_ha_value_from_percentage_brightness(increased_percentage)
    #                 },
    #             }
    #             self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
    #             self.speak_dialog("acknowledge")
    #         else:
    #             self.speak_dialog("lights.status.not.available", data={"device": device})
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    # @intent_handler("lights.decrease.brightness.intent")
    # def handle_decrease_brightness_intent(self, message):
    #     device, device_id = self._get_device_from_message(message)
    #     if device and device_id:  # If the intent doesn't understand the device, you'll get a device_id but no device
    #         brightness = self._get_device_info(device_id).get("attributes", {}).get("brightness")
    #         if brightness:
    #             decreased_percentage = max(self._get_percentage_brightness_from_ha_value(brightness) - 10, 0)
    #             call_data = {
    #                 "device_id": device_id,
    #                 "function_name": "turn_on",
    #                 "function_args": {
    #                     "brightness": self._get_ha_value_from_percentage_brightness(decreased_percentage)
    #                 },
    #             }
    #             self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
    #             self.speak_dialog("acknowledge")
    #         else:
    #             self.speak_dialog("lights.status.not.available", data={"device": device})
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    # @intent_handler("lights.get.color.intent")
    # def handle_get_color_intent(self, message):
    #     device, device_id = self._get_device_from_message(message)
    #     color = self._get_device_info(device_id).get("attributes", {}).get("rgb_color")
    #     LOG.info(device)
    #     LOG.info(device_id)
    #     if device_id:
    #         for dev in self.devices_list:
    #             if dev["id"] == device_id:
    #                 color = dev["attributes"].get("rgb_color")
    #                 LOG.info(dev)
    #                 if color:
    #                     self.speak_dialog("lights.current.color", data={"color": color, "device": device})
    #                 else:
    #                     self.speak_dialog("lights.status.not.available", data={"device": device, "status": "color"})

    # @intent_handler("lights.set.color.intent")
    # def handle_set_color_intent(self, message):
    #     device, device_id = self._get_device_from_message(message)
    #     if device and device_id:
    #         dev = self._get_device_info(device_id)
    #         brightness = dev.get("attributes", {}).get("brightness")

    #         call_data = {
    #             "device_id": device_id,
    #             "function_name": "turn_on",
    #             "data": {"brightness": brightness, "rgb_color": message.data.get("color")},
    #         }
    #         self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
    #         self.speak_dialog("acknowledge")
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    @intent_handler("show.area.dashboard.intent")
    def handle_show_area_dashboard_intent(self, message):
        area = message.data.get("area")
        if area:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.show.area.dashboard", {"area": area}))
            self.speak_dialog("area.dashboard.opened", data={"area": area})
        else:
            self.speak_dialog("area.not.found")

    @intent_handler("assist.intent")
    def handle_assist_intent(self, message):
        command = message.data.get("command")
        if command:
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.assist.intent", {"command": command}))
            self.speak_dialog("assist")
        else:
            self.speak("Sorry, I didn't catch what to tell Home Assistant.")

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
    #                 self.log.info(call_data)
    #                 self.bus.emit(Message("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
    #             self.speak_dialog("acknowledge")
    #         else:
    #             self.speak("vacuum.action.not.found", data={"action": action})
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    def _handle_assist_error(self, _):
        self.speak("Home Assistant returned an error. Please check the enclosure or PHAL logs for more information.")
