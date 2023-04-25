import wx
from bot import brain
from prompts import Prompt
from ocr import OCR, ScreenCapture
from AppKit import NSAlert

if __name__ == "__main__":
    app = ScreenCapture()
    app.MainLoop()

    ocr = OCR()
    res = "".join(ocr.ocr_img('.tmp.ocr.screentest.png'))
    conversation = []
    conversation.append(Prompt.english_speaker.value)
    conversation.append({
        "role": "user",
        "content": res
    })
    alert = NSAlert.alloc().init()
    alert.setMessageText_(brain(conversation))
    alert.addButtonWithTitle_("已阅")
    alert.runModal()