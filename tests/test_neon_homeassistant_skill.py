import pytest

from neon_homeassistant_skill import HomeAssistantSkill

class TestSomething(pytest.TestCase):
    @classmethod
    def setup_class(cls, self):
        self.ha = HomeAssistantSkill()

    def test_something(self):
        self.assertEqual("hello", self.var)
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("A. Musing", "Hello A. Musing!"),
            ("traveler", "Hello traveler!"),
            ("projen developer", "Hello projen developer!"),
        ],
    )
    def test_hello(self, name, expected):
        """Example test with parametrization."""
        assert name == expected
