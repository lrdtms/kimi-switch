#!/usr/bin/env python3
"""Switch Claude Code between Anthropic and Moonshot Kimi by editing settings.json env.

Usage: kimi_switch.py <on|off|status> [--key KEY] [--settings PATH] [--profile PATH]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
BASE_URL = "https://api.moonshot.ai/anthropic"
MAIN = "kimi-k3[1m]"
HAIKU = "kimi-k2.7-code"

PRESET = {
    "ANTHROPIC_BASE_URL": BASE_URL,
    "ANTHROPIC_MODEL": MAIN,
    "ANTHROPIC_DEFAULT_OPUS_MODEL": MAIN,
    "ANTHROPIC_DEFAULT_SONNET_MODEL": MAIN,
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": HAIKU,
    "ANTHROPIC_DEFAULT_FABLE_MODEL": MAIN,
    "CLAUDE_CODE_SUBAGENT_MODEL": MAIN,
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "CLAUDE_CODE_EFFORT_LEVEL": "max",
}

# Everything Kimi setup may have written; `off` removes exactly these (Kimi docs' cleanup list).
MANAGED = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_SMALL_FAST_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME",
    "ANTHROPIC_DEFAULT_FABLE_MODEL",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME",
    "ENABLE_TOOL_SEARCH",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW",
    "CLAUDE_CODE_EFFORT_LEVEL",
]


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def load_settings(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{path} is not valid JSON ({e}); nothing was changed.")
    if not isinstance(data, dict):
        die(f"{path} is not a JSON object; nothing was changed.")
    return data


def save_settings(path, data):
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".bak"))
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mask(key):
    return f"...{key[-4:]}" if key and len(key) > 4 else "(set)"


def load_key(profile):
    if profile.exists():
        try:
            return json.loads(profile.read_text(encoding="utf-8")).get("api_key")
        except (json.JSONDecodeError, AttributeError):
            return None
    return None


def cmd_on(settings_path, profile, key):
    if key:
        profile.write_text(json.dumps({"api_key": key}, indent=2) + "\n", encoding="utf-8")
    else:
        key = load_key(profile)
    if not key:
        die("No Moonshot API key saved. Re-run with --key YOUR_KEY "
            "(create one at https://platform.kimi.ai/console/api-keys).")
    data = load_settings(settings_path)
    env = data.setdefault("env", {})
    env.pop("ANTHROPIC_API_KEY", None)  # conflicts with AUTH_TOKEN
    env.update(PRESET)
    env["ANTHROPIC_AUTH_TOKEN"] = key
    save_settings(settings_path, data)
    print(f"Kimi ON ({MAIN}, haiku={HAIKU}). Restart Claude Code, then run /status.")
    print("kimi-k2.7-code needs thinking enabled (Alt+T). Don't commit settings.json - it holds your key.")


def cmd_off(settings_path):
    data = load_settings(settings_path)
    env = data.get("env")
    removed = [k for k in MANAGED if isinstance(env, dict) and env.pop(k, None) is not None]
    if isinstance(env, dict) and not env:
        del data["env"]
    save_settings(settings_path, data)
    print(f"Kimi OFF (removed {len(removed)} vars). Restart Claude Code; your saved /login applies again.")
    print("Your Kimi key stays in the profile file for the next 'on'.")


def cmd_status(settings_path):
    env = load_settings(settings_path).get("env") or {}
    url = env.get("ANTHROPIC_BASE_URL")
    if url == BASE_URL:
        print(f"Kimi: ON\n  base url: {url}\n  model:    {env.get('ANTHROPIC_MODEL')}\n"
              f"  key:      {mask(env.get('ANTHROPIC_AUTH_TOKEN'))}")
    elif url:
        print(f"Kimi: OFF (custom base url set: {url})")
    else:
        print("Kimi: OFF (using default Anthropic endpoint)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["on", "off", "status"])
    p.add_argument("--key")
    p.add_argument("--settings", type=Path, default=CLAUDE_DIR / "settings.json")
    p.add_argument("--profile", type=Path, default=CLAUDE_DIR / "kimi-profile.json")
    a = p.parse_args()
    if a.action == "on":
        cmd_on(a.settings, a.profile, a.key)
    elif a.action == "off":
        cmd_off(a.settings)
    else:
        cmd_status(a.settings)


if __name__ == "__main__":
    main()
