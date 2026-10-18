# Vendored support files for the installed skills

Some skills in `.claude/skills/` drive a whole project rather than just giving instructions. These are lean copies of
those projects, without the demo videos and showcase media.

| Skills | Needs | Where |
|---|---|---|
| `video-toolkit`, `ltx2`, `qwen-edit`, `ideogram4`, `acestep`, `elevenlabs`, `runpod`, `moviepy`, `playwright-recording`, `video-toolkit-remotion` (name: `remotion`) | the toolkit's `tools/*.py`, run with `uv run tools/...` from the toolkit root | `claude-code-video-toolkit/` (upstream: github.com/digitalsamba/claude-code-video-toolkit) |
| `motionloom` | the p5.js engine project (`npm install`, `npm run ...`, `node engine/tools/render.mjs`) | `motionloom-studio/`: copy it into a new project folder and work there |

The `video-toolkit` skill expects the toolkit at `~/.openclaw/workspace/claude-code-video-toolkit`. In a fresh container, recreate the link:

    mkdir -p ~/.openclaw/workspace && ln -sfn "$PWD/.claude/vendor/claude-code-video-toolkit" ~/.openclaw/workspace/claude-code-video-toolkit

Most toolkit tools also need accounts and keys (Modal or RunPod GPUs, ElevenLabs, Ideogram...). Put them in the toolkit's
`.env`, starting from `.env.example`, and never commit it. Nothing is configured yet.

Skipped: the toolkit's `remotion-official` skill, an older copy of `remotion-best-practices` (installed from the
official Remotion pack).
