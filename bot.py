import os
import sys
import uuid
import openai
import logging
import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk 
from dotenv import load_dotenv
from playsound import playsound
# from ISR.models import RDN
R = sr.Recognizer()
M = sr.Microphone()

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

load_dotenv(dotenv_path)
logging.basicConfig(level=logging.INFO)

LOCALHOST_SOLUTION = os.environ.get("LOCALHOST_SOLUTION")
AZURE_SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION")
AZURE_SPEECH_TO_TEXT_LANG = os.environ.get("AZURE_SPEECH_TO_TEXT_LANG")
AZURE_SPEECH_AUDIO_SAVE_TO_LOCAL = os.environ.get("AZURE_SPEECH_AUDIO_SAVE_TO_LOCAL")
openai.api_type = os.environ.get("AZURE_OPENAI_API_TYPE")
openai.api_base = os.environ.get("AZURE_OPENAI_API_BASE")
openai.api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
openai.api_key = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT_MODEL")
AZURE_OPENAI_MODEL_TEMPERATURE = float(os.environ.get("AZURE_OPENAI_MODEL_TEMPERATURE"))
AZURE_OPENAI_MODEL_MAX_TOKEN = int(os.environ.get("AZURE_OPENAI_MODEL_MAX_TOKEN"))
MAGIC_WORD_TO_END_CHAT = os.environ.get("MAGIC_WORD_TO_END_CHAT")

if LOCALHOST_SOLUTION == "False":
    logging.info("IF YOU HAVE GPU ON LAPTOP, YOU CAN SETTING LOCALSOLUTION WAS True.")
    # you can use bark & whisper

if AZURE_SPEECH_AUDIO_SAVE_TO_LOCAL == "True":
    logging.info("WE WILL SAVE THE AUDIO FILE TO LOCAL PATH")

# HOTWORD = "奥特曼"

def listen_to_me_use_whisper(recognizer, audio):
    try:
        out = recognizer.recognize_whisper(audio, model="large", language="chinese")
        return out
    except sr.UnknownValueError:
        logging.error(sr.UnknownValueError)
    except sr.RequestError as e:
        logging.error(sr.RequestError)

def listen_to_me_use_azure(r, a):
    try:
        out = r.recognize_azure(a, location="eastus", language="zh-CN", key=AZURE_SPEECH_KEY)
        if len(out) == 2:
            return out[0]
        return None
    except sr.UnknownValueError:
        logging.error(sr.UnknownValueError)
    except sr.RequestError as e:
        logging.error(sr.RequestError)

# def tell_to_me_use_bark(text_prompt):
#     audio_array = generate_audio(text_prompt)
    # filename = os.path.join(os.path.dirname(__file__), "audio", str(uuid.uuid4()) + ".wav")
#     write_wav(filename, SAMPLE_RATE, audio_array)
#     playsound(filename)

def tell_to_me_use_azure(text_prompt): 
    # if you don't want save to local, you can modify this code
    endpoint = AZURE_SPEECH_REGION  
    filename = os.path.join(os.path.dirname(__file__), "audio", str(uuid.uuid4()) + ".wav")
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=endpoint)  
    audio_output = speechsdk.audio.AudioOutputConfig(filename=filename) 
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)  
  
    result = speech_synthesizer.speak_text_async(text_prompt).get()  
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:  
        logging.info("Azure: Text to Speech Successed")
        playsound(filename)
    else:
        logging.error("Azure: Text to speech failed. {result.error_details}")

def listen_to_me(r, m):
    with m as source:
        audio = r.listen(source, timeout=5)
        if LOCALHOST_SOLUTION == "False":
            out = listen_to_me_use_azure(r, audio)
        else:
            out = listen_to_me_use_whisper(r, audio)
        logging.info("I: {}".format(out))
        return out

def brain(content):
    try:
        response = openai.ChatCompletion.create(
            engine=AZURE_OPENAI_DEPLOYMENT_MODEL,
            messages=content,
            max_tokens=2048,
            n=1,
            temperature=0.5,
        )
        assistant_response = response.choices[0].message["content"]
    except:
        logging.error("Can't Get Response From Azure")
        return None
    return assistant_response

# klug mean smart in German, this function has context with brain
def klug(context, keep=False, talktome=False):
    result = brain(context)
    logging.info("BOT: {}".format(result))
    if talktome:
        tell_to_me_use_azure(result)
    if keep:
        context.append({
            "role": "assistant",
            "content": result})
        context = context[-10:]
        while True:
            res = listen_to_me(R, M)
            if res:
                if MAGIC_WORD_TO_END_CHAT in res:
                    logging.info("Bot: Ended The Converstion")
                    sys.exit()
                context.append({
                    "role": "user",
                    "content": res
                })
                break
            else:
                logging.info("I didn't hear what you were saying")
        return klug(context, True, True)
    return result