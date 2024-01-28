# pylint: disable=missing-function-docstring,missing-class-docstring,missing-module-docstring,logging-fstring-interpolation
from typing import List

from ovos_bus_client import Message
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


def chunks(lst, n_len) -> List[list]:
    """Split list into n-length chunks."""
    n_len = max(1, n_len)
    return [lst[i : i + n_len] for i in range(0, len(lst), n_len)]


DEFAULT_SETTINGS: dict = {
    "connected": True,
}


# https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant/blob/master/ovos_PHAL_plugin_homeassistant/__init__.py
class NeonHomeAssistantSkill(OVOSSkill):
    """Home Assistant skill for Neon OS. Requires the PHAL Home Assistant plugin."""

    _intents_registered = True
    connected_intents = (
        "sensor.intent",
        "turn.on.intent",
        "turn.off.intent",
        "stop.intent",
        "lights.get.brightness.intent",
        "lights.set.brightness.intent",
        "lights.increase.brightness.intent",
        "lights.decrease.brightness.intent",
        "lights.get.color.intent",
        "lights.set.color.intent",
        "show.area.dashboard.intent",
        "assist.intent",
    )

    @property
    def connected(self) -> bool:
        if self._connected is False:
            self._connected = self.on_ready(  # pylint: disable=attribute-defined-outside-init
                Message(
                    "ovos.phal.plugin.homeassistant.check_connected",
                    {},
                    {"skill_id": self.skill_id},
                )
            )
        return self._connected

    def initialize(self):
        # Register bus handlers
        self.bus.on("mycroft.ready", self.on_ready)
        self.bus.on(
            "ovos.phal.plugin.homeassistant.assist.message.response",
            self._handle_assist_error,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.get.device.response",
            self.handle_get_device_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.device.turn_on.response",
            self.handle_turn_on_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.device.turn_off.response",
            self.handle_turn_off_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.get.light.brightness.response",
            self.handle_get_light_brightness_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.set.light.brightness.response",
            self.handle_set_light_brightness_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.increase.light.brightness.response",
            self.handle_set_light_brightness_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.decrease.light.brightness.response",
            self.handle_set_light_brightness_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.get.light.color.response",
            self.handle_get_light_color_response,
        )
        self.bus.on(
            "ovos.phal.plugin.homeassistant.set.light.color.response",
            self.handle_set_light_color_response,
        )
        self.settings.merge(DEFAULT_SETTINGS, new_only=True)
        self.bus.on("ovos.phal.plugin.homeassistant.ready", self.on_ready)
        self._connected = self.settings.get("connected", False)  # pylint: disable=attribute-defined-outside-init
        self._handle_connection_state(self.connected)

    def _handle_connection_state(self, connected_to_plugin: bool):
        if connected_to_plugin and self._intents_registered is False:
            self.log.info("Home Assistant PHAL plugin connected! Registering intents.")
            self.enable_ha_intents()
            self._intents_registered = True
        if not connected_to_plugin and self._intents_registered is True:
            self.log.info("Home Assistant PHAL plugin not connected! Disabling intents.")
            self.disable_ha_intents()
            self._intents_registered = False
        if connected_to_plugin and self._connected is True:
            self.log.info("Home Assistant PHAL plugin reports connected, but intents are already registered.")
        if not connected_to_plugin and self._connected is False:
            self.log.info("Home Assistant PHAL plugin did not report connected, and intents are already disabled.")

    def enable_ha_intents(self):
        for intent in self.connected_intents:
            success = self.enable_intent(intent)
            if not success:
                self.log.error(f"Error registering intent: {intent}")
            else:
                self.log.info(f"Successfully registered intent: {intent}")

    def disable_ha_intents(self):
        for intent in self.connected_intents:
            self.intent_service.remove_intent(intent)
            try:
                assert self.intent_service.intent_is_detached(intent) is True
            except AssertionError:
                self.log.error(f"Error disabling intent: {intent}")

    def on_ready(self, message):
        resp = self.bus.wait_for_response(message.forward("ovos.phal.plugin.homeassistant.check_connected"), timeout=1)
        response = resp.data if resp else None
        self.log.debug(f"Response from HA PHAL plugin: {response}")
        if resp and resp.data.get("connected"):
            self._handle_connection_state(connected_to_plugin=True)
            return True
        if not resp:
            self._handle_connection_state(connected_to_plugin=False)
            return False

        self.log.info("PHAL Plugin not connected to HomeAssistant")
        self.disable_ha_intents()
        return False

    # Handlers
    @intent_handler("sensor.intent")  # pragma: no cover
    def get_device_intent(self, message):
        """Handle intent to get a single device status from Home Assistant."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.get.device",
                    {"device": device},
                    {"skill_id": self.skill_id},
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

    @intent_handler("turn.on.intent")  # pragma: no cover
    def handle_turn_on_intent(self, message) -> None:
        """Handle turn on intent."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.device.turn_on",
                    {"device": device},
                    {"skill_id": self.skill_id},
                )
            )
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

    @intent_handler("turn.off.intent")  # pragma: no cover
    @intent_handler("stop.intent")  # pragma: no cover
    def handle_turn_off_intent(self, message) -> None:
        """Handle turn off intent."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.device.turn_off",
                    {"device": device},
                    {"skill_id": self.skill_id},
                )
            )
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

    @intent_handler("open.dashboard.intent")  # pragma: no cover
    def handle_open_dashboard_intent(self, _):
        self.bus.emit(Message("ovos-PHAL-plugin-homeassistant.home", None, {"skill_id": self.skill_id}))
        self.speak_dialog("ha.dashboard.opened")

    @intent_handler("close.dashboard.intent")  # pragma: no cover
    def handle_close_dashboard_intent(self, _):
        self.bus.emit(
            Message(
                "ovos-PHAL-plugin-homeassistant.close",
                None,
                {"skill_id": self.skill_id},
            )
        )
        self.speak_dialog("ha.dashboard.closed")

    @intent_handler("lights.get.brightness.intent")  # pragma: no cover
    def handle_get_brightness_intent(self, message):
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.get.light.brightness",
                    {"device": device},
                    {"skill_id": self.skill_id},
                )
            )
        else:
            self.speak_dialog("no.parsed.device")

    def handle_get_light_brightness_response(self, message):
        brightness = message.data.get("brightness")
        device = message.data.get("device")
        self.log.info(f"Device {device} brightness is {brightness}")
        if brightness:
            self.speak_dialog(
                "lights.current.brightness",
                data={
                    "brightness": brightness,
                    "device": device,
                },
            )
        if message.data.get("response"):
            self.speak_dialog("device.not.found", data={"device": device})
        else:
            self.speak_dialog("lights.status.not.available", data={"device": device})

    @intent_handler("lights.set.brightness.intent")  # pragma: no cover
    def handle_set_brightness_intent(self, message: Message):
        self.log.info(message.data)
        device = message.data.get("entity")
        brightness = message.data.get("brightness")
        if device and brightness:
            call_data = {
                "device": device,
                "function_name": "turn_on",
                "brightness": self._get_ha_value_from_percentage_brightness(brightness),
            }
            self.log.info(call_data)
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.set.light.brightness",
                    call_data,
                    message.context,
                )
            )
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_set_light_brightness_response(self, message):
        """Handle set light brightness response. Works for increasing/decreasing or setting explicitly."""
        brightness = message.data.get("brightness")
        device = message.data.get("device")
        self.log.info(f"Device {device} brightness is now {brightness}")
        if brightness:
            return self.speak_dialog(
                "lights.current.brightness",
                data={
                    "brightness": brightness,
                    "device": device,
                },
            )
        if message.data.get("response"):
            return self.speak_dialog("device.not.found", data={"device": device})
        else:
            return self.speak_dialog("lights.status.not.available", data={"device": device})

    @intent_handler("lights.increase.brightness.intent")  # pragma: no cover
    def handle_increase_brightness_intent(self, message):
        self.log.info(message.data)
        device = message.data.get("entity")
        if device:
            call_data = {"device": device}
            self.log.info(call_data)
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.increase.light.brightness",
                    call_data,
                    message.context,
                )
            )
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("no.parsed.device")

    @intent_handler("lights.decrease.brightness.intent")  # pragma: no cover
    def handle_decrease_brightness_intent(self, message):
        self.log.info(message.data)
        device = message.data.get("entity")
        if device:
            call_data = {"device": device}
            self.log.info(call_data)
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.decrease.light.brightness",
                    call_data,
                    message.context,
                )
            )
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("no.parsed.device")

    # Light color
    @intent_handler("lights.get.color.intent")  # pragma: no cover
    def handle_get_color_intent(self, message):
        self.log.info(message.data)
        device = message.data.get("entity")
        if device:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.get.light.color",
                    {"device": device},
                    {"skill_id": self.skill_id},
                )
            )
        else:
            self.speak_dialog("no.parsed.device")

    def handle_get_light_color_response(self, message):
        color = message.data.get("color")
        device = message.data.get("device")
        self.log.info(f"Device {device} color is {color}")
        if color:
            return self.speak_dialog(
                "lights.current.color",
                data={
                    "color": color,
                    "device": device,
                },
            )
        if message.data.get("response"):
            return self.speak_dialog("device.not.found", data={"device": device})
        else:
            return self.speak_dialog("lights.status.not.available", data={"device": device})

    @intent_handler("lights.set.color.intent")  # pragma: no cover
    def handle_set_color_intent(self, message: Message):
        self.log.info(message.data)
        device = message.data.get("entity")
        color = message.data.get("color")
        if device and color:
            call_data = {
                "device": device,
                "color": color,
            }
            self.log.info(call_data)
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.set.light.color",
                    call_data,
                    message.context,
                )
            )
            self.speak_dialog("acknowledge")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_set_light_color_response(self, message):
        """Handle set light color response."""
        color = message.data.get("color")
        device = message.data.get("device")
        self.log.info(f"Device {device} color is now {color}")
        if color:
            return self.speak_dialog(
                "lights.current.color",
                data={
                    "color": color,
                    "device": device,
                },
            )
        if message.data.get("response"):
            return self.speak_dialog("device.not.found", data={"device": device})
        else:
            return self.speak_dialog("lights.status.not.available", data={"device": device})

    @intent_handler("show.area.dashboard.intent")  # pragma: no cover
    def handle_show_area_dashboard_intent(self, message):
        area = message.data.get("area")
        if area:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.show.area.dashboard",
                    {"area": area},
                    {"skill_id": self.skill_id},
                )
            )
            self.speak_dialog("area.dashboard.opened", data={"area": area})
        else:
            self.speak_dialog("area.not.found")

    @intent_handler("assist.intent")  # pragma: no cover
    def handle_assist_intent(self, message):
        """Handle passthrough to Home Assistant's Assist API."""
        command = message.data.get("command")
        if command:
            self.bus.emit(
                Message(
                    "ovos.phal.plugin.homeassistant.assist.intent",
                    {"command": command},
                    {"skill_id": self.skill_id},
                )
            )
            self.speak_dialog("assist")
        else:
            self.speak_dialog("assist.not.understood")

    # @intent_handler("vacuum.action.intent")  # TODO: Find an intent that doesn't conflict with OCP  # pragma: no cover
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

    def _get_ha_value_from_percentage_brightness(self, brightness):
        return round(int(brightness)) / 100 * 255


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    NeonHomeAssistantSkill(bus=FakeBus(), skill_id="neon_homeassistant_skill.test")
