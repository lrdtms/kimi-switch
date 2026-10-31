---
name: kimi-switch
description: Switch Claude Code between Anthropic and the Moonshot Kimi API by adding or removing the Kimi env block in ~/.claude/settings.json. Use whenever the user wants to turn Kimi/Moonshot on or off, "use kimi", "switch to kimi", "go back to Claude/Anthropic", check which provider or endpoint is active, or edit ANTHROPIC_BASE_URL / ANTHROPIC_AUTH_TOKEN, even if they don't say "skill".
---

# kimi-switch

Claude Code only honors one API credential at a time. Kimi is enabled by putting its endpoint, key, and model names in the `env` block of `~/.claude/settings.json` (that block overrides shell env vars, so it is the only place that matters). This skill toggles that block with a script so nothing else in settings.json (permissions, hooks, other env vars like `KIE_AI_API_KEY`) is touched.

## Commands

Run with `python ~/.claude/skills/kimi-switch/scripts/kimi_switch.py <action>`:

| User intent | Action |
|---|---|
| Turn Kimi on | `on` (add `--key KEY` the first time or to replace the key) |
| Turn Kimi off / back to Anthropic | `off` |
| Which provider is active? | `status` |

- `on` uses the saved key in `~/.claude/kimi-profile.json`. If the script says no key is saved, ask the user for their Moonshot key (create one at https://platform.kimi.ai/console/api-keys), then re-run with `--key`. The key is saved so later toggles don't need it.
- `off` removes only the Kimi-managed vars and keeps the saved key for next time.
- A rolling backup is written to `settings.json.bak` before every change.

## After running

1. Tell the user to restart Claude Code; env changes only apply on startup.
2. Suggest `/status` to confirm: base URL `https://api.moonshot.ai/anthropic` and model `kimi-k3[1m]` when on.
3. When on, `kimi-k2.7-code` (haiku tier) requires thinking enabled (Alt+T), otherwise requests fail with `400 invalid thinking`.

## Rules

- Never print the full API key back to the user; `status` masks it.
- If switching doesn't seem to take effect, check for stale `ANTHROPIC_*` exports in shell profiles or Windows user environment variables.
- Remind the user not to commit settings.json or kimi-profile.json (plaintext key).
- Optional endpoint check: `curl https://api.moonshot.ai/anthropic/v1/messages -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{"model":"kimi-k3.1-pro","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}'` (a 401 means a bad key).
