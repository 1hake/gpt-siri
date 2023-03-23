import sys
import pyaudio
import wave
import os
import openai
from google.cloud import texttospeech
from google.cloud import speech
import io
import pygame
import keyboard
import pyperclip
import re

API_URL = "https://api.openai.com/v1/chat/completions"

# Microphone stream config.
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 20
WAVE_OUTPUT_FILENAME = "output.wav"
MP3_OUTPUT_FILENAME = "output.mp3"


"""
- selectionne mode automator 
- rentre une commande audio 
- ecris un prompt avant cette commande qui dit "ecris un script qui fait ceci"
- parse la reponse de gpt pour extraire le code 
- execute le code
- enregistre le resultat dans un fichier
"""

filepath = sys.argv[1]
mode = ''
if (len(sys.argv) > 2):
    mode = sys.argv[2]
    

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
    clipboard_content = ''
    if mode == 'c':
        clipboard_content = pyperclip.paste()
        print(clipboard_content)

    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        prompt = result.alternatives[0].transcript
        if mode == 'c':
            prompt += f':\n{clipboard_content}'
        if mode == 'a':
            automator_content = "Écris un script Applescript qui realise au mieux la demande suivant. Lorsqu'on te demande quelque chose qui necessite d'aller sur le web ouvre google chrome avec la page suivante: https://www.google.com/search?q= et tape la demande dans la barre de recherche de maniere pertinente. Repond juste un bloc de code sans explication."
            prompt = f'{automator_content}:\n{prompt}'
            


        owc(u'\nYou ask:\n{}'.format(prompt))
        owc("Waiting for ChatGPT to respond...")
        chat = get_gpt4_response(prompt)
        owc(f'\nChatGPT says:\n {chat}')
        if mode == 'a':
            #applescript = re.search(regex, chat).group().strip("```")
            #owc(f"-------------------------------------\n{applescript} \n-------------------------------------\n")
            # execute applescript
            chat = chat.replace('end tell', '\nend tell\n')
            owc(f"-------------------------------------\n{chat} \n-------------------------------------\n")
            os.system(f'osascript -e "{chat}"')
            
            
        texttospeech_gcp(chat)


def texttospeech_gcp(text):
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
        speaking_rate=1.4
    )
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # The response's audio_content is binary.
    with open(MP3_OUTPUT_FILENAME, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)

def record() -> None:
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    owc("* recording")
    owc("Press space to stop recording")

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if keyboard.is_pressed('space'):
            break
    owc("* done recording")

    # Properly stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data to a WAV file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# Send the prompt to GPT-4 and get the response
def get_gpt4_response(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu parle en français"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0]['message']['content']


def play_audio_from_mp3():
    pygame.mixer.init()
    pygame.mixer.music.load(MP3_OUTPUT_FILENAME)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        if keyboard.is_pressed('space'):
            pygame.mixer.music.stop()
            break
        continue


def owc(text, filepath=filepath):
    text = '\n' + text + '\n'
    print(text)
    f = open(filepath, 'a')
    f.write(text)
    f.close()


def main():
    record()
    stt_gcp()
    play_audio_from_mp3()

if __name__ == '__main__':
    main()