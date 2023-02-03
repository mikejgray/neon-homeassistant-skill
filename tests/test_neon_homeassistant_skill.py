import unittest
from unittest.mock import create_autospec

from neon_homeassistant_skill import NeonHomeAssistantSkill


class Bus:
    def emit(x):
        print(x)


class TestNeonHASkill(unittest.TestCase):
    def setUp(self):
        self.ha = create_autospec(NeonHomeAssistantSkill)
        self.ha.bus = Bus()

    def test_handle_open_dashboard_intent(self):
        self.ha.handle_open_dashboard_intent("")
        self.ha.bus.emit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
