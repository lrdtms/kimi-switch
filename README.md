# kimi-switch

Claude Code skill that switches between Anthropic and the Moonshot Kimi API by
adding or removing the Kimi env block in `~/.claude/settings.json`.

- `SKILL.md` – skill definition
- `scripts/kimi_switch.py` – `on | off | status` toggle

Install: copy this folder to `~/.claude/skills/kimi-switch`.

Never commit `~/.claude/settings.json` or `~/.claude/kimi-profile.json` (plaintext API key).
