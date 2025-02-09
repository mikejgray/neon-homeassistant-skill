# pylint: disable=missing-function-docstring,missing-class-docstring,missing-module-docstring,logging-fstring-interpolation
from ovos_bus_client import Message
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


class NeonHomeAssistantSkill(OVOSSkill):
    """Home Assistant skill for Neon OS. Requires the PHAL Home Assistant plugin."""

    _intents_enabled = True
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

    def initialize(self):
        # Register bus handlers
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
        if self.disable_intents:
            self.log.info("User has indicated they do not want to use Home Assistant intents. Disabling.")
            self.disable_ha_intents()

    @property
    def verbose(self):
        return self.settings.get("verbose", False)

    @verbose.setter
    def verbose(self, value):
        self.settings["verbose"] = value

    @property
    def silent_entities(self):
        return set(self.settings.get("silent_entities", []))

    @silent_entities.setter
    def silent_entities(self, value):
        self.settings["silent_entities"] = value

    @property
    def disable_intents(self):
        setting = self.settings.get("disable_intents", False)
        self._handle_connection_state(setting)
        return setting

    @disable_intents.setter
    def disable_intents(self, value):
        self.settings["disable_intents"] = value
        self._handle_connection_state(value)

    def _handle_connection_state(self, disable_intents: bool):
        if self._intents_enabled and disable_intents is True:
            self.log.info(
                "Disabling Home Assistant intents by user request. To re-enable, set disable_intents to False."
            )
            self.disable_ha_intents()
        if not self._intents_enabled and disable_intents is False:
            self.log.info("Enabling Home Assistant intents by user request. To disable, set disable_intents to True.")
            self.enable_ha_intents()

    def enable_ha_intents(self):
        for intent in self.connected_intents:
            success = self.enable_intent(intent)
            if not success:
                self.log.error(f"Error registering intent: {intent}")
            else:
                self.log.info(f"Successfully registered intent: {intent}")
        self._intents_enabled = True

    def disable_ha_intents(self):
        for intent in self.connected_intents:
            self.intent_service.remove_intent(intent)
            try:
                assert self.intent_service.intent_is_detached(intent) is True
            except AssertionError:
                self.log.error(f"Error disabling intent: {intent}")
        self._intents_enabled = False

    # Handlers

    @intent_handler("get.all.devices.intent")  # pragma: no cover
    def handle_rebuild_device_list(self, message: Message):
        self.bus.emit(
            message.forward(
                "ovos.phal.plugin.homeassistant.rebuild.device.list",
                None,
            )
        )
        self.speak_dialog("acknowledge")

    @intent_handler("enable.intent")  # pragma: no cover
    def handle_enable_intent(self, message: Message):
        self.settings["disable_intents"] = False
        self.speak_dialog("enable")
        self.enable_ha_intents()

    @intent_handler("disable.intent")  # pragma: no cover
    def handle_disable_intent(self, message: Message):
        self.settings["disable_intents"] = True
        self.speak_dialog("disable")
        self.disable_ha_intents()

    @intent_handler("sensor.intent")  # pragma: no cover
    def get_device_intent(self, message: Message):
        """Handle intent to get a single device status from Home Assistant."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(message.forward("ovos.phal.plugin.homeassistant.get.device", {"device": device}))
            if self.verbose:
                self.speak_dialog("acknowledge")
            else:
                self.log.info(f"Trying to get device status for {device}")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_get_device_response(self, message: Message):
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
    def handle_turn_on_intent(self, message: Message) -> None:
        """Handle turn on intent."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.device.turn_on",
                    {"device": device},
                )
            )
            if self.verbose:
                self.speak_dialog("acknowledge")
            else:
                self.log.info(f"Trying to turn on device {device}")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_turn_on_response(self, message: Message) -> None:
        """Handle turn on intent response."""
        self.log.debug(f"Handling turn on response to {message.data}")
        device = message.data.get("device", "")
        if device and device not in self.silent_entities:
            self.speak_dialog("device.turned.on", data={"device": device})
        else:
            self.speak_dialog("no.parsed.device")

    @intent_handler("turn.off.intent")  # pragma: no cover
    @intent_handler("stop.intent")  # pragma: no cover
    def handle_turn_off_intent(self, message: Message) -> None:
        """Handle turn off intent."""
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.device.turn_off",
                    {"device": device},
                )
            )
            if self.verbose:
                self.speak_dialog("acknowledge")
            else:
                self.log.info(f"Trying to turn off device {device}")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_turn_off_response(self, message: Message) -> None:
        self.log.debug(f"Handling turn off response to {message.data}")
        device = message.data.get("device", "")
        if device and device not in self.silent_entities:
            self.speak_dialog("device.turned.off", data={"device": device})
        else:
            self.speak_dialog("no.parsed.device")

    @intent_handler("open.dashboard.intent")  # pragma: no cover
    def handle_open_dashboard_intent(self, message: Message):
        self.bus.emit(message.forward("ovos-PHAL-plugin-homeassistant.home", None))
        self.speak_dialog("ha.dashboard.opened")

    @intent_handler("close.dashboard.intent")  # pragma: no cover
    def handle_close_dashboard_intent(self, message: Message):
        self.bus.emit(
            message.forward(
                "ovos-PHAL-plugin-homeassistant.close",
                None,
            )
        )
        self.speak_dialog("ha.dashboard.closed")

    @intent_handler("lights.get.brightness.intent")  # pragma: no cover
    def handle_get_brightness_intent(self, message: Message):
        self.log.info(message.data)
        device = message.data.get("entity", "")
        if device:
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.get.light.brightness",
                    {"device": device},
                )
            )
        else:
            self.speak_dialog("no.parsed.device")

    def handle_get_light_brightness_response(self, message: Message):
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
                message.forward(
                    "ovos.phal.plugin.homeassistant.set.light.brightness",
                    call_data,
                )
            )
            if self.verbose:
                self.speak_dialog("acknowledge")
            else:
                self.log.info(f"Trying to set brightness for {device}")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_set_light_brightness_response(self, message: Message):
        """Handle set light brightness response. Works for increasing/decreasing or setting explicitly."""
        brightness = message.data.get("brightness")
        device = message.data.get("device")
        self.log.info(f"Device {device} brightness is now {brightness}")
        if brightness and device not in self.silent_entities:
            return self.speak_dialog(
                "lights.current.brightness",
                data={
                    "brightness": brightness,
                    "device": device,
                },
            )
        if device in self.silent_entities:
            return
        if message.data.get("response"):
            return self.speak_dialog("device.not.found", data={"device": device})
        else:
            return self.speak_dialog("lights.status.not.available", data={"device": device})

    @intent_handler("lights.increase.brightness.intent")  # pragma: no cover
    def handle_increase_brightness_intent(self, message: Message):
        self.log.info(message.data)
        device = message.data.get("entity")
        if device:
            call_data = {"device": device}
            self.log.info(call_data)
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.increase.light.brightness",
                    call_data,
                )
            )
            if self.verbose:
                self.speak_dialog("acknowledge")
            else:
                self.log.info(f"Trying to increase brightness for {device}")
        else:
            self.speak_dialog("no.parsed.device")

    @intent_handler("lights.decrease.brightness.intent")  # pragma: no cover
    def handle_decrease_brightness_intent(self, message: Message):
        self.log.info(message.data)
        device = message.data.get("entity")
        if device:
            call_data = {"device": device}
            self.log.info(call_data)
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.decrease.light.brightness",
                    call_data,
                )
            )
            if self.verbose:
                self.speak_dialog("acknowledge")
            else:
                self.log.info(f"Trying to decrease brightness for {device}")
        else:
            self.speak_dialog("no.parsed.device")

    # Light color
    @intent_handler("lights.get.color.intent")  # pragma: no cover
    def handle_get_color_intent(self, message: Message):
        self.log.info(message.data)
        device = message.data.get("entity")
        if device:
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.get.light.color",
                    {"device": device},
                )
            )
        else:
            self.speak_dialog("no.parsed.device")

    def handle_get_light_color_response(self, message: Message):
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
                message.forward(
                    "ovos.phal.plugin.homeassistant.set.light.color",
                    call_data,
                )
            )
            if self.verbose:
                self.speak_dialog("acknowledge")
            else:
                self.log.info(f"Trying to set color of {device}")
        else:
            self.speak_dialog("no.parsed.device")

    def handle_set_light_color_response(self, message: Message):
        """Handle set light color response."""
        color = message.data.get("color")
        device = message.data.get("device")
        self.log.info(f"Device {device} color is now {color}")
        if color and device not in self.silent_entities:
            return self.speak_dialog(
                "lights.current.color",
                data={
                    "color": color,
                    "device": device,
                },
            )
        if device in self.silent_entities:
            return
        if message.data.get("response"):
            return self.speak_dialog("device.not.found", data={"device": device})
        else:
            return self.speak_dialog("lights.status.not.available", data={"device": device})

    @intent_handler("show.area.dashboard.intent")  # pragma: no cover
    def handle_show_area_dashboard_intent(self, message: Message):
        area = message.data.get("area")
        if area:
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.show.area.dashboard",
                    {"area": area},
                )
            )
            self.speak_dialog("area.dashboard.opened", data={"area": area})
        else:
            self.speak_dialog("area.not.found")

    @intent_handler("assist.intent")  # pragma: no cover
    def handle_assist_intent(self, message: Message):
        """Handle passthrough to Home Assistant's Assist API."""
        command = message.data.get("command")
        if command:
            self.bus.emit(
                message.forward(
                    "ovos.phal.plugin.homeassistant.assist.intent",
                    {"command": command},
                )
            )
            if self.verbose:
                self.speak_dialog("assist")
            else:
                self.log.info(f"Trying to pass message to Home Assistant's Assist API:\n{command}")
        else:
            self.speak_dialog("assist.not.understood")

    # @intent_handler("vacuum.action.intent")  # TODO: Find an intent that doesn't conflict with OCP  # pragma: no cover
    # def handle_vacuum_action_intent(self, message: Message):
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
    #                 self.bus.emit(message.forward("ovos.phal.plugin.homeassistant.call.supported.function", call_data))
    #             if self.verbose:
    #                 self.speak_dialog("acknowledge")
    #             else:
    #                 self.log.info("Trying to execute action on vacuum cleaner")
    #         else:
    #             self.speak("vacuum.action.not.found", data={"action": action})
    #     else:
    #         self.speak_dialog("device.not.found", data={"device": device})

    def _handle_assist_error(self, _):
        self.speak_dialog("assist.error")

    def _get_ha_value_from_percentage_brightness(self, brightness):
        return round(int(brightness)) / 100 * 255


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    NeonHomeAssistantSkill(bus=FakeBus(), skill_id="neon_homeassistant_skill.test")
