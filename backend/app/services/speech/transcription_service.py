from __future__ import annotations

import requests

from app.core.config.settings import settings


class TranscriptionError(RuntimeError):
    pass


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribes raw audio bytes directly (no download needed) using
    Groq's free Whisper Large v3 endpoint. Used by the mic-recording
    feature in the command input, where the browser already has the
    audio bytes in memory. Chosen over ElevenLabs here because it
    requires no separate paid API key - it reuses GROQ_API_KEY, which
    is already configured for text generation.
    """
    if not settings.GROQ_API_KEY:
        raise TranscriptionError(
            "GROQ_API_KEY is not configured, cannot transcribe audio."
        )

    files = {
        "file": (filename, audio_bytes, "application/octet-stream"),
    }
    data = {
        "model": "whisper-large-v3",
        "response_format": "json",
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers=headers,
        data=data,
        files=files,
        timeout=120,
    )

    if response.status_code != 200:
        raise TranscriptionError(
            f"Groq Whisper STT failed ({response.status_code}): {response.text[:500]}"
        )

    payload = response.json()
    text = payload.get("text", "")

    if not text:
        raise TranscriptionError("Groq Whisper STT returned empty text.")

    return text.strip()


def normalize_transcript_script(text: str) -> str:
    """
    Whisper transcribes Urdu speech inconsistently - sometimes in Urdu
    script (Nastaliq), sometimes Roman Urdu, sometimes drifting into
    English mid-sentence - with no reliable way to force one script via
    the STT API itself. This runs one fast, cheap LLM call AFTER
    transcription to normalize the script:
      - Urdu-script speech  -> rewritten in Roman Urdu (transliteration,
        NOT translation - the words/meaning stay exactly the same)
      - Already Roman Urdu  -> left as Roman Urdu
      - English speech      -> left as proper English
    Never changes the actual words or meaning, only the script/spelling
    system, so command routing and downstream content are unaffected.
    Falls back to the original raw text if this call fails for any
    reason - a skipped normalization is far better than losing the
    transcript entirely.
    """
    if not text.strip():
        return text

    if not settings.GROQ_API_KEY:
        return text

    system_prompt = (
        "You fix speech-to-text output's script/spelling ONLY - you never "
        "translate or change the meaning or wording.\n"
        "Rules:\n"
        "1. If the text is written in Urdu script (Nastaliq) OR in "
        "Devanagari script (Hindi letters - Whisper sometimes mistakes "
        "spoken Urdu/Roman-Urdu-accented speech for Hindi and outputs "
        "Devanagari), rewrite the exact same spoken words in Roman Urdu "
        "(Latin letters) - transliterate the sounds, do not translate the "
        "meaning, and do not treat it as if it were actually Hindi content.\n"
        "2. If the text is already in Roman Urdu, return it unchanged "
        "(only fix obvious spelling glitches from transcription).\n"
        "3. If the text is in English, return it unchanged.\n"
        "4. Never introduce formal/literary Hindi vocabulary or keep "
        "Devanagari characters in the output - the final output must be "
        "in Latin letters (Roman Urdu) or English only, never Devanagari "
        "or Nastaliq script.\n"
        "5. Output ONLY the corrected text - no explanation, no quotes, "
        "no preamble."
    )

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        normalized = data["choices"][0]["message"]["content"].strip()
        return normalized if normalized else text
    except Exception:
        return text


def transcribe_audio_url(url: str) -> str:
    """
    Downloads the audio at `url` and transcribes it to text using
    ElevenLabs Speech-to-Text (Scribe). Called from a worker thread
    (via asyncio.to_thread) since it uses blocking requests calls.
    """
    if not settings.ELEVENLABS_API_KEY:
        raise TranscriptionError(
            "ELEVENLABS_API_KEY is not configured, cannot transcribe audio."
        )

    audio_resp = requests.get(url, timeout=60)
    audio_resp.raise_for_status()
    audio_bytes = audio_resp.content

    files = {
        "file": ("audio.webm", audio_bytes, "application/octet-stream"),
    }
    data = {
        "model_id": "scribe_v1",
    }
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
    }

    response = requests.post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        headers=headers,
        data=data,
        files=files,
        timeout=120,
    )

    if response.status_code != 200:
        raise TranscriptionError(
            f"ElevenLabs STT failed ({response.status_code}): {response.text[:500]}"
        )

    payload = response.json()
    text = payload.get("text", "")

    if not text:
        raise TranscriptionError("ElevenLabs STT returned empty text.")

    return text.strip()