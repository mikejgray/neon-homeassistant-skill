# Home Assistant Neon Skill

Uses [PHAL Home Assistant plugin](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant)

Available on PyPi: `pip install neon-homeassistant-skill`

## Installation on Neon

\***\*Note\*\***: This skill and the required PHAL plugin come pre-installed on Neon images for the Mycroft Mark II and Neon's published Docker images. These instructions are for custom development builds or creating your own Neon instance from scratch.

Install ovos-PHAL-plugin-homeassistant [per their documentation](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant)

Then, you can `pip install neon-homeassistant-skill`, or handle the installation from the `~/.config/neon/neon.yaml` file if you prefer:

```yaml
skills:
  default_skills:
    # Jokes skill included because it cannot be pip installed to the image
    - https://github.com/JarbasSkills/skill-icanhazdadjokes/tree/dev
    - neon-homeassistant-skill # Optionally with a version, such as neon-homeassistant-skill==0.0.10
```

### Authenticating to Home Assistant

On a device with a screen, such as the Mycroft Mark II, you can say `open home assistant dashboard` and use the OAuth login flow to authenticate from the PHAL plugin. If you don't have a screen available or prefer to edit the configuration directly, read on.

---

The documentation for ovos-PHAL-plugin-homeassistant specifies which configuration file to put your Home Assistant hostname/port and API key. Note that Neon uses a YAML configuration, not a JSON file, so edit `~/.config/neon/neon.yaml` and make the following update for a minimal installation:

```yaml
PHAL:
  ovos-PHAL-plugin-homeassistant:
    host: http://<HA_IP_OR_HOSTNAME>:8123
    api_key: <HA_LONG_LIVED_TOKEN>
```

The `PHAL` node above should be at the root of the Neon user configuration file, appended to the end of file if existing content exists, and will merge with system configuration per [Neon Configuration Docs.](https://neongeckocom.github.io/neon-docs/quick_reference/configuration/)

Mycroft Mark II does not always support .local hostnames such as the default `homeassistant.local` DNS. You may need to use the IP of your Home Assistant instance instead. If you have a Nabu Casa subscription and don't mind traffic going out to the internet using your public Nabu Casa DNS is also a supported option. However, if your internet connectivity drops from your Neon instance, you will be unable to control your smart home devices from Neon. A local DNS/IP is preferable.

## Upcoming Features

- Start OAuth workflow with voice
- Start an instance of the ovos-PHAL-plugin-homeassistant if PHAL isn't already running
- Vacuum functions
- HVAC functions
