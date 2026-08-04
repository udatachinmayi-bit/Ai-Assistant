# Voice System

Everything audio. Sub-modules: `wake_word/` (always-on wake word detection), `stt/` (speech-to-text), `tts/` (text-to-speech), `audio_io/` (shared mic/speaker I/O). Each sub-module implements an interface defined in `core/interfaces`, so the underlying engine (e.g. Whisper vs Vosk) can be swapped via config.
