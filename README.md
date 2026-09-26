# Coder-Bot

## CLI

Start the API and bot with `./start.sh`, then launch the terminal UI:

```bash
CODER_API_KEY=cb-your-key python3 coder-cli/cli.py
```

Set `CODER_API_URL` when the API runs on another host. The UI supports `ask`,
`code`, `plan`, `debug`, `exec`, `history`, `sysinfo`, and `api-status`.

## Raspberry Pi

Inside the UI, run `rpi-config` once to save the Pi hostname/IP, SSH user, and
port. Then use `rpi <command>` or `rpi-status`; every remote command requires
explicit confirmation and uses the local SSH keys/agent.
# coder-bot
