from __future__ import annotations

"""
Enterprise Fallback Registry

This file contains ONLY fallback order. Every id below is verified
against MODEL_REGISTRY (see the audit that produced this file) --
no dead/unregistered ids, so FallbackResolver never silently skips
past a broken entry and gives up early.

Ordering strategy per category:
  1. Fastest/cheapest native provider first (e.g. Groq for text).
  2. Other native providers next, for real cross-provider redundancy
     (so one provider running out of credits doesn't fail the whole
     request).
  3. OpenRouter variants last, as a broad safety net that can reach
     many underlying models through a single aggregator key.

Adding a new provider/model should only require:
  1. Register the model in MODEL_REGISTRY
  2. Add its id here (optional, but recommended for redundancy)
"""

FALLBACK_REGISTRY: dict[str, tuple[str, ...]] = {

    # =====================================================
    # TEXT
    # =====================================================
    "text": (
        "llama-4-scout",              # groq - fastest
        "llama-3.3-70b",              # groq
        "gpt-5.5",                    # openai
        "claude-sonnet-4",            # anthropic
        "gemini-2.5-pro",             # gemini
        "grok-4",                     # xai
        "mistral-large",              # mistral
        "deepseek-chat",              # deepseek
        "qwen3-32b",                  # groq
        "openrouter-gpt-5.5",         # openrouter - broad safety net
        "openrouter-claude-sonnet-4", # openrouter
        "openrouter-gemini-2.5-pro",  # openrouter
        "openrouter-auto",            # openrouter - last resort
    ),

    # =====================================================
    # IMAGE
    # =====================================================
    "image": (
        "flux-pro",
        "flux-dev",
        "flux-schnell",
        "ideogram-v3",
        "recraft-v3",
        "imagen-4",
        "gpt-image-1",
        "replicate-flux-pro",
        "replicate-flux-dev",
        "replicate-sdxl",
        "flux-1-dev-together",
        "openrouter-flux",
        "sogni-z-image-turbo",
    ),
    "thumbnail": (
        "flux-pro",
        "flux-dev",
        "flux-schnell",
        "ideogram-v3",
        "imagen-4",
        "gpt-image-1",
        "sogni-z-image-turbo",
    ),
    "poster": (
        "flux-pro",
        "flux-dev",
        "ideogram-v3",
        "imagen-4",
        "gpt-image-1",
    ),
    "banner": (
        "flux-pro",
        "flux-dev",
        "ideogram-v3",
        "imagen-4",
    ),
    "logo": (
        "flux-pro",
        "ideogram-v3",
        "flux-dev",
        "recraft-v3",
    ),
    "profile_photo": (
        "flux-pro",
        "imagen-4",
        "flux-dev",
    ),
    "cover": (
        "flux-pro",
        "flux-dev",
        "imagen-4",
    ),

    # =====================================================
    # VIDEO
    # =====================================================
    "video": (
        "veo-3",
        "runway-gen4",
        "kling-v2",
        "runway-gen3-alpha",
        "kling-v1.6",
        "pika-2.2",
        "pika-2.1",
        "cogvideox",
        "svd-xt",
        "pixverse-v4",
    ),

    # =====================================================
    # AUDIO
    # =====================================================
    "audio": (
        "eleven-multilingual-v2",
        "eleven-turbo-v2",
        "fish-s2.1-pro",
    ),
    "voice": (
        "eleven-multilingual-v2",
        "eleven-turbo-v2",
    ),

    # =====================================================
    # SPEECH TO TEXT
    # =====================================================
    "transcription": (
        "eleven-scribe-v1",
        "gemini-2.5-flash",
    ),

    # =====================================================
    # EMBEDDINGS
    # =====================================================
    # No embedding models are registered in MODEL_REGISTRY yet.
    # Leave empty until one is added, rather than pointing at ids
    # that don't exist.
    "embedding": (),
}
