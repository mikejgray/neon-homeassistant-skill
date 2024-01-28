#!/usr/bin/env python3
import tomllib
from setuptools import setup

with open ("pyproject.toml", "rb", encoding="utf-8") as file:
    pyproject = tomllib.load(file)
if not pyproject:
    raise ValueError("No pyproject.toml found, please create one!")
__version__ = pyproject.get("tool-poetry", {}).get("version")
if not __version__:
    raise ValueError("No version found in pyproject.toml, please update!")
setup(
    name="neon-homeassistant-skill",
    version=__version__,
    entry_points={
        "ovos.plugin.skill": "neon_homeassistant_skill.mikejgray=neon_homeassistant_skill:NeonHomeAssistantSkill"
        }
    )
