# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,protected-access
from ovos_utils.messagebus import FakeBus
from neon_homeassistant_skill import NeonHomeAssistantSkill


def test_default_enabled_state():
    bus = FakeBus()
    skill = NeonHomeAssistantSkill(bus=bus, skill_id="neon_homeassistant_skill.test")
    assert set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})
    assert skill._intents_enabled is True



def test_intent_disable_setting():
    bus = FakeBus()
    skill = NeonHomeAssistantSkill(
        bus=bus, skill_id="neon_homeassistant_skill.test", settings={"disable_intents": True}
    )
    assert skill.disable_intents is True
    assert not set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})


def test_reenabling():
    bus = FakeBus()
    skill = NeonHomeAssistantSkill(
        bus=bus, skill_id="neon_homeassistant_skill.test", settings={"disable_intents": True}
    )
    assert skill.disable_intents is True
    assert not set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})
    skill.settings["disable_intents"] = False
    assert skill.disable_intents is False
    assert skill._intents_enabled is True
    assert set(skill.connected_intents).issubset({intent[0] for intent in skill.intent_service.registered_intents})
