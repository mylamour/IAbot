import sys
from prompts import Prompt
import speech_recognition as sr
from bot import listen_to_me, klug

R = sr.Recognizer()
M = sr.Microphone()

conversation = []

if sys.argv[1] == "interview":
    conversation.append(Prompt.interview.value)

if sys.argv[1] == "speaker":
    conversation.append(Prompt.english_speaker.value)

speak = False
if speak:
    first = listen_to_me(R, M)
else:
    first = "Hi"

conversation.append({
    "role": "user",
    "content": first
})

klug(conversation, keep=True, talktome=True)
