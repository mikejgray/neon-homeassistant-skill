# Home Assistant Neon Skill

Uses [PHAL Home Assistant plugin](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant)

Still a work in progress - PRs and issues welcome

Available on PyPi: `pip install neon-homeassistant-skill`

## Installation on Neon

Install ovos-PHAL-plugin-homeassistant [per their documentation](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant)
Note that Neon uses a YAML configuration, not a JSON file, so edit ~/.config/neon/neon.yaml and make the following update for a minimal installation:

```yaml
PHAL:
  ovos-PHAL-plugin-homeassistant:
    host: http://<HA_IP_OR_HOSTNAME>:8123
    api_key: <HA_LONG_LIVED_TOKEN>
```

You can also say `open home assistant dashboard` on a device with a screen, like the Mark 2, and use the OAuth login flow from the PHAL plugin.

SSH to the Neon device

```shell
osm install https://github.com/mikejgray/neon-homeassistant-skill
```

## Upcoming Features

- Start OAuth workflow with voice
- Start an instance of the ovos-PHAL-plugin-homeassistant if PHAL isn't already running
- Vacuum functions
- HVAC functions
