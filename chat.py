import sys
import logging
from prompts import Prompt
import speech_recognition as sr
from core import listen_to_me, brain, tell_to_me_use_azure, MAGIC_WORD_TO_END_CHAT

R = sr.Recognizer()
M = sr.Microphone()
conversation = []

# klug has context with brain
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
            res = listen_to_me(R,M)
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