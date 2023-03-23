# use user micropone to record voice and send to google speech api

import pyaudio
import wave
import urllib3
import json
import time
import os
import sys

import openai
import requests

from google.cloud import speech
import io

# Google speech api
GOOGLE_SPEECH_URL = 'http://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium'

# Microphone stream config.
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"


def stt_gcp():
    """Transcribe the given audio file."""
    client = speech.SpeechClient()

    with io.open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="fr-FR",
        speech_contexts=[speech.SpeechContext(
            phrases=[],
            boost=0
        )]
    )

    response = client.recognize(config=config, audio=audio)
    print("Done\n")
    for result in response.results:
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))
        chat = get_gpt4_response(result.alternatives[0].transcript)
        print(chat)
        texttospeech_gcp(chat)


def texttospeech_gcp(text):
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient()
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="fr-FR", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL        
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.5
    )
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

    


def record() -> None:
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


API_URL = "https://api.openai.com/v1/chat/completions"

# Send the prompt to GPT-4 and get the response
def get_gpt4_response(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    # response = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt=prompt,
    #     max_tokens=3000,
    # )
    return response.choices[0]['message']['content']


def play_audio_from_mp3():
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


def main():
    record()
    stt_gcp()
    play_audio_from_mp3()


if __name__ == '__main__':
    main()
    #texttospeech_gcp("allez bonsoir comment ca va trop cool")
    #play_audio_from_mp3()

