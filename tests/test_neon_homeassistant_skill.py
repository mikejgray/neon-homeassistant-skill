import unittest
from unittest.mock import create_autospec

from neon_homeassistant_skill import NeonHomeAssistantSkill


class TestNeonHASkill(unittest.TestCase):
    def test_get_device_intent(self):
        ha = create_autospec(NeonHomeAssistantSkill)
        ha._get_device_intent("ovos.phal.plugin.homeassistant.get.device", "living room light")
        ha._get_device_intent.assert_called_once()


if __name__ == "__main__":
    unittest.main()
