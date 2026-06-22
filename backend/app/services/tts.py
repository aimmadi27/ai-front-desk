from google.cloud import texttospeech


_client: texttospeech.TextToSpeechClient | None = None


def get_client() -> texttospeech.TextToSpeechClient:
    global _client
    if _client is None:
        _client = texttospeech.TextToSpeechClient()
    return _client


def synthesize_speech(text: str, language: str = "en") -> bytes:
    client = get_client()
    lang_code = "es-US" if language == "es" else "en-US"
    voice_name = "es-US-Neural2-A" if language == "es" else "en-US-Neural2-F"

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=lang_code,
        name=voice_name,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )
    return response.audio_content
