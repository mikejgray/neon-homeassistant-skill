from time import sleep
from unittest.mock import Mock
from ovos_utils.messagebus import FakeBus, Message
from neon_homeassistant_skill import NeonHomeAssistantSkill
from ovos_PHAL_plugin_homeassistant import HomeAssistantPlugin


def test_default_disconnected_state():
    bus = FakeBus()
    plugin = HomeAssistantPlugin(bus=bus)
    skill = NeonHomeAssistantSkill(bus=bus, skill_id="neon_homeassistant_skill.test", settings={"connected": False})
    assert skill.connected is False
    sleep(2)  # Allow the intents to deregister
    assert not set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})
    return bus, plugin, skill

def test_settings_connected_state():
    bus = FakeBus()
    HomeAssistantPlugin(bus=bus)
    skill = NeonHomeAssistantSkill(bus=bus, skill_id="neon_homeassistant_skill.test", settings={"connected": True})
    assert skill.connected is True
    assert set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})

def test_connected_state():
    bus = FakeBus()
    plugin = HomeAssistantPlugin(bus=bus)
    skill = NeonHomeAssistantSkill(bus=bus, skill_id="neon_homeassistant_skill.test", settings={"connected": False})
    plugin.instance_available = True
    assert skill.connected is True
    assert set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})

def test_registering_from_disconnected():
    """Test disconnected, then connect, and make sure the intents are registered"""
    _, plugin, skill = test_default_disconnected_state()
    plugin.instance_available = True
    assert skill.connected is True
    sleep(2)
    assert set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})

def test_handle_connected_message_after_init():
    bus = FakeBus()
    skill = NeonHomeAssistantSkill(bus=bus, skill_id="neon_homeassistant_skill.test", settings={"connected": False})
    assert skill.connected is False
    assert not set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})
    sleep(2)
    bus.wait_for_response = Mock(return_value=Message("does.not.matter", {"connected": True}, {}))
    skill.on_ready(Message("", {"connected": True}, {}))
    sleep(2)
    assert skill.connected is True
    assert set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})

def test_handle_not_connected_message_after_init():
    bus = FakeBus()
    skill = NeonHomeAssistantSkill(bus=bus, skill_id="neon_homeassistant_skill.test", settings={"connected": False})
    assert skill.connected is False
    assert not set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})
    sleep(2)
    bus.wait_for_response = Mock(return_value=Message("does.not.matter", {"connected": False}, {}))
    skill.on_ready(Message("", {"connected": True}, {}))
    sleep(2)
    assert skill.connected is False
    assert not set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})
