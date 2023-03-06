import json
import unittest
from pathlib import Path
from os import getenv, listdir, path
from os.path import exists
from shutil import rmtree
from typing import List, Pattern, Set
from yaml import safe_load

from ovos_skills_manager import SkillEntry
from ovos_utils.messagebus import FakeBus
from padacioso import IntentContainer
from neon_homeassistant_skill import NeonHomeAssistantSkill

branch = "main"
repo = "neon-homeassistant-skill"
author = "mikejgray"
url = f"https://github.com/{author}/{repo}@{branch}"


class TestOSM(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.skill_id = "{repo.lower()}.{author.lower()}"

    def test_osm_github_install(self):
        skill = SkillEntry.from_github_url(url)
        tmp_skills = "/tmp/osm_installed_skills"
        skill_folder = f"{tmp_skills}/{skill.uuid}"

        if exists(skill_folder):
            rmtree(skill_folder)

        updated = skill.install(folder=tmp_skills, default_branch=branch)
        self.assertEqual(updated, True)
        self.assertTrue(exists(skill_folder))

        updated = skill.install(folder=tmp_skills, default_branch=branch)
        self.assertEqual(updated, False)


class TestSkillLoading(unittest.TestCase):
    """
    Test skill loading, intent registration, and language support. Test cases
    are generic, only class variables should be modified per-skill.
    """

    # Static parameters
    bus = FakeBus()
    messages: List[str] = list()
    test_skill_id = "neon-homeassistant-skill"
    # Default Core Events
    default_events = [
        "mycroft.skill.enable_intent",
        "mycroft.skill.disable_intent",
        "mycroft.skill.set_cross_context",
        "mycroft.skill.remove_cross_context",
        "intent.service.skills.deactivated",
        "intent.service.skills.activated",
        "mycroft.skills.settings.changed",
        "skill.converse.ping",
        "skill.converse.request",
        f"{test_skill_id}.activate",
        f"{test_skill_id}.deactivate",
    ]

    skill = NeonHomeAssistantSkill()

    # Specify valid languages to test
    supported_languages = ["en-us"]

    adapt_intents = set()
    # regex entities, not necessarily filenames
    regex: Set[Pattern] = set()
    # Specify skill intents as sets
    padatious_intents = listdir(Path("neon_homeassistant_skill/vocab/en-us"))
    for i, intent in enumerate(padatious_intents):
        padatious_intents[i] = intent
    padatious_intents = set(padatious_intents)
    # dialog is .dialog file basenames (case-sensitive)
    dialog = listdir(Path("neon_homeassistant_skill/dialog/en-us"))
    for i, d in enumerate(dialog):
        dialog[i] = d[:-7].replace(".intent", "")
    vocab = None  # Not in this skill

    @classmethod
    def setUpClass(cls) -> None:
        cls.bus.on("message", cls._on_message)
        cls.skill.config_core["secondary_langs"] = cls.supported_languages
        cls.skill._startup(cls.bus, cls.test_skill_id)
        cls.adapt_intents = {f"{cls.test_skill_id}:{intent}" for intent in cls.adapt_intents}
        cls.padatious_intents = {f"{cls.test_skill_id}:{intent}" for intent in cls.padatious_intents}

    @classmethod
    def _on_message(cls, message):
        cls.messages.append(json.loads(message))

    def test_skill_setup(self):
        print(f"skill id: {self.skill.skill_id}")
        self.assertEqual(self.skill.skill_id, self.test_skill_id)
        for msg in self.messages:
            self.assertEqual(msg.get("context", {}).get("skill_id", ""), self.test_skill_id)

    def test_intent_registration(self):
        registered_adapt = list()
        registered_padatious = dict()
        registered_vocab = dict()
        registered_regex = dict()
        for msg in self.messages:
            if msg["type"] == "register_intent":
                registered_adapt.append(msg["data"]["name"])
            elif msg["type"] == "padatious:register_intent":
                lang = msg["data"]["lang"]
                registered_padatious.setdefault(lang, list())
                registered_padatious[lang].append(msg["data"]["name"])
            elif msg["type"] == "register_vocab":
                lang = msg["data"]["lang"]
                if msg["data"].get("regex"):
                    registered_regex.setdefault(lang, dict())
                    regex = (
                        msg["data"]["regex"]
                        .split("<", 1)[1]
                        .split(">", 1)[0]
                        .replace(self.test_skill_id.replace(".", "_"), "")
                        .lower()
                    )
                    registered_regex[lang].setdefault(regex, list())
                    registered_regex[lang][regex].append(msg["data"]["regex"])
                else:
                    registered_vocab.setdefault(lang, dict())
                    voc_filename = msg["data"]["entity_type"].replace(self.test_skill_id.replace(".", "_"), "").lower()
                    registered_vocab[lang].setdefault(voc_filename, list())
                    registered_vocab[lang][voc_filename].append(msg["data"]["entity_value"])
        self.assertEqual(set(registered_adapt), self.adapt_intents)
        for lang in self.supported_languages:
            if self.padatious_intents:
                set_difference = set(registered_padatious[lang]).difference(set(self.padatious_intents))
                self.assertEqual(set_difference, set())
            if self.vocab:
                self.assertEqual(set(registered_vocab[lang].keys()), self.vocab)
            if self.regex:
                self.assertEqual(set(registered_regex[lang].keys()), self.regex)
                for rx in self.regex:
                    # Ensure every vocab file has exactly one entry
                    self.assertTrue(all((rx in line for line in registered_regex[lang][rx])))

    def test_skill_events(self):
        events = self.default_events + list(self.adapt_intents)
        for event in events:
            self.assertIn(event, [e[0] for e in self.skill.events])

    def test_dialog_files(self):
        for lang in self.supported_languages:
            for dialog in self.dialog:
                file = self.skill.find_resource(f"{dialog}.dialog", "dialog", lang)
                self.assertTrue(path.isfile(file))


class TestSkillIntentMatching(unittest.TestCase):
    skill = NeonHomeAssistantSkill()

    test_intents_filename = getenv("INTENT_TEST_FILE", "tests/test_intents.yaml")
    with open(test_intents_filename) as f:
        valid_intents = safe_load(f)
    ha_intents = IntentContainer()
    for lang, intents in valid_intents.items():
        for name, utt in valid_intents[lang].items():
            if type(utt[0]) == str:
                u = utt
            else:
                u = []
                for sentence, entity in utt[0].items():
                    if "entity" in entity[0].keys():
                        revised_intent = sentence.replace(entity[0].get("entity"), "{entity}")
                        if len(entity[0].keys()) > 1 and entity[0].get("color"):
                            revised_intent = revised_intent.replace(entity[0].get("color"), "{color}")
                        u.append(revised_intent)
                    elif "area" in entity[0].keys():
                        u.append(sentence.replace(entity[0].get("area"), "{area}"))
            ha_intents.add_intent(name, u)

    from mycroft.skills.intent_service import IntentService

    bus = FakeBus()
    intent_service = IntentService(bus)
    test_skill_id = "test_skill.test"

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill.config_core["secondary_langs"] = list(cls.valid_intents.keys())
        cls.skill._startup(cls.bus, cls.test_skill_id)

    def test_intents(self):
        for lang in self.valid_intents.keys():
            for intent, examples in self.valid_intents[lang].items():
                for utt in examples:
                    if type(utt) == str:
                        result = self.ha_intents.calc_intent(utt)
                        self.assertTrue(result.get("conf") >= 0.9)
                        self.assertEqual(result.get("name"), intent)
                    else:
                        u = list(utt.keys())[0]
                        result = self.ha_intents.calc_intent(u)
                        if len(utt[u]) > 1:
                            self.assertTrue(list(utt[u][1].values())[0] in u)
