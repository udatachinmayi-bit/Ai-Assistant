# Models

Local AI model artifacts (weights, tokenizers, ONNX/GGUF files) for:
- `llm/` — local language model files (if using a local LLM backend instead of/alongside a cloud API)
- `stt/` — speech-to-text model files (e.g. Whisper checkpoints)
- `tts/` — text-to-speech voice models
- `wake_word/` — wake word detector model files (e.g. custom "Hey Chinu" model)
- `vision/` — vision/detection model files

Model files are **gitignored** — they are downloaded/fetched via a setup script, not committed to source control.
Each subfolder should eventually contain a `MANIFEST.md` or `manifest.json` describing the exact model version/source used.
