
import os
import azure.cognitiveservices.speech as speechsdk

# Required: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
# Optional: AZURE_SPEECH_VOICE (default ja-JP-NanamiNeural), AZURE_SPEECH_RATE, AZURE_SPEECH_PITCH

VOICE = os.getenv("AZURE_SPEECH_VOICE", "ja-JP-NanamiNeural")
RATE = os.getenv("AZURE_SPEECH_RATE", "+0%")
PITCH = os.getenv("AZURE_SPEECH_PITCH", "+0Hz")

def synthesize_to_wav(text: str) -> bytes:
    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")
    if not key or not region:
        raise RuntimeError("AZURE_SPEECH_KEY / AZURE_SPEECH_REGION is not set")

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )
    ssml = f"""<speak version='1.0' xml:lang='ja-JP'>
  <voice name='{VOICE}'>
    <prosody rate='{RATE}' pitch='{PITCH}'>{text or '入力が取得できませんでした。もう一度お願いします。'}</prosody>
  </voice>
</speak>"""
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_ssml_async(ssml).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return bytes(result.audio_data)
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = speechsdk.CancellationDetails(result)
        raise RuntimeError(f"Azure TTS canceled: {details.reason} {details.error_details}")
    else:
        raise RuntimeError("Azure TTS unknown failure")
