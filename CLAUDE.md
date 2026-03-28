# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Markdown Document Translator — an LLM-based tool that translates Markdown files by slicing them at level-1 headers (`# `) and translating each slice sequentially or concurrently.

## Commands

```bash
# Install dependencies (recommended: use uv)
uv venv && .venv/Scripts/activate && uv pip install -r requirements.txt

# Run translation from CLI
python main.py input.md

# Run with custom config/env
python main.py input.md -c config.yaml -e .env

# Run GUI
python gui_main.py

# Run tests
pytest

# Run a single test
pytest tests/test_slicer.py
```

## Architecture

### Processing Pipeline

```
main.py → ConfigLoader → MarkdownSlicer → Translator → Assembler → output.md
              ↓                              ↓
           .env API key              ThreadPoolExecutor (configurable concurrency)
```

1. **Input validation** — file exists, UTF-8 encoding check
2. **Slice** — split document by `# ` (ATX-style level-1 headers only, exact `# ` pattern)
3. **Translate** — each slice sent to LLM via OpenAI Compatible API; concurrent execution via `ThreadPoolExecutor`
4. **Assemble** — join slices with `"\n\n"` separator; failed slices preserve original content
5. **Output** — `{input}_translated.md` in same directory

### Key Modules

| Module | Responsibility |
|--------|----------------|
| `core/translator.py` | `Translator` class — orchestrates slices, manages concurrency, logs progress. `TranslationResult` holds slices + errors + duration |
| `core/slicer.py` | `MarkdownSlicer` — regex `^# ` splits doc; `Slice` dataclass with `index`, `content`, `is_header_only` |
| `core/assembler.py` | `Assembler.assemble()` — joins slice strings with `"\n\n"` |
| `api/client.py` | `APIClient` wraps OpenAI SDK; `APIError` for errors; 1 automatic retry on timeout/rate-limit |
| `api/prompt_builder.py` | `PromptBuilder` — substitutes `{content}` placeholder in prompt template |
| `config/loader.py` | `ConfigLoader` merges `config.yaml` (api/concurrency/prompt) + `.env` (API key) |

### Concurrency

- Default concurrency = 1 (sequential). Configured via `config.yaml` or `concurrency` field
- `Translator._translate_concurrent()` uses `ThreadPoolExecutor` with `max_workers=concurrency`
- Each thread creates its own `APIClient` instance

### Error Handling

- Slice translation failure → original content preserved in output
- `APIClient` raises `APIError` (status_code-aware); translator catches and logs
- `main()` returns exit code 1 if any translation errors occurred

## Configuration

`config.yaml`:
```yaml
api:
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 2048
concurrency: 1
prompt: |
  {content} is substituted with slice content
```

`.env`: `OPENAI_API_KEY=sk-...`

## Slicing Rules

- Pattern: `^# ` (hash, space, at line start) — MULTILINE mode
- Content before first header becomes the first slice
- Each `# ` header + its content until next `# ` is one slice
- No headers found → entire document is single slice
