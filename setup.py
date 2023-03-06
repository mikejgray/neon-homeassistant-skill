#!/usr/bin/env python3
from setuptools import setup
import os
from os import walk, path

BASEDIR = path.abspath(path.dirname(__file__))
URL = "https://github.com/mikejgray/neon-homeassistant-skill"
SKILL_CLAZZ = "NeonHomeAssistantSkill"  # needs to match __init__.py class name
PYPI_NAME = "neon-homeassistant-skill"  # pip install PYPI_NAME

# below derived from github url to ensure standard skill_id
SKILL_AUTHOR, SKILL_NAME = URL.split(".com/")[-1].split("/")
SKILL_PKG = SKILL_NAME.lower().replace("-", "_")
PLUGIN_ENTRY_POINT = f"{SKILL_NAME.lower()}.{SKILL_AUTHOR.lower()}={SKILL_PKG}:{SKILL_CLAZZ}"
# skill_id=package_name:SkillClass


def get_requirements(requirements_filename: str):
    requirements_file = path.join(path.abspath(path.dirname(__file__)), requirements_filename)
    with open(requirements_file, "r", encoding="utf-8") as r:
        requirements = r.readlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith("#")]
    if "MYCROFT_LOOSE_REQUIREMENTS" in os.environ:
        print("USING LOOSE REQUIREMENTS!")
        requirements = [r.replace("==", ">=").replace("~=", ">=") for r in requirements]
    return requirements


def find_resource_files():
    resource_base_dirs = ("locale", "ui", "dialog", "vocab")
    base_dir = path.dirname(__file__)
    package_data = ["*.json"]
    for res in resource_base_dirs:
        if path.isdir(path.join(base_dir, res)):
            for directory, _, files in walk(path.join(base_dir, res)):
                if files:
                    package_data.append(path.join(directory.replace(base_dir, "").lstrip("/"), "*"))
    return package_data


with open("README.md", "r") as f:
    long_description = f.read()

with open("./version.py", "r", encoding="utf-8") as v:
    for line in v.readlines():
        if line.startswith("__version__"):
            if '"' in line:
                version = line.split('"')[1]
            else:
                version = line.split("'")[1]

setup(
    name=PYPI_NAME,
    version=version,
    description="OVOS home assistant phal plugin voice interface skill",
    long_description=long_description,
    url=URL,
    author="Mike Gray",
    author_email="mike@graywind.org",
    license="Apache-2.0",
    package_dir={SKILL_PKG: ""},
    package_data={SKILL_PKG: find_resource_files()},
    packages=[SKILL_PKG],
    include_package_data=True,
    install_requires=get_requirements("requirements.txt"),
    keywords="ovos home assistant phal voice interface skill plugin",
    entry_points={"ovos.plugin.skill": PLUGIN_ENTRY_POINT},
)
