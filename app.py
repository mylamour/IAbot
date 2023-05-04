import rumps
import logging
import subprocess as sp
from core import LOCALHOST_SOLUTION, AZURE_SPEECH_AUDIO_SAVE_TO_LOCAL

if LOCALHOST_SOLUTION == "False":
    logging.info("IF YOU HAVE GPU ON LAPTOP, YOU CAN SETTING LOCALSOLUTION WAS True.")
    # you can use bark & whisper

if AZURE_SPEECH_AUDIO_SAVE_TO_LOCAL == "True":
    logging.info("WE WILL SAVE THE AUDIO FILE TO LOCAL PATH")

class OAI(rumps.App):
    def __init__(self):
        super(OAI, self).__init__("AIBOT", icon="icon.png")   

    # @rumps.clicked("聊天","随便聊聊", callback=False)
    # def aichat(self, _):
        # sp.Popen('python chat.py aichat', shell=True)

    @rumps.clicked("聊天","模拟面试")
    def interview(self, _):
        # sp.call is blocking but Popen is Non-Blocking
        sp.Popen('python chat.py interview', shell=True)

    @rumps.clicked("聊天","口语聊天")
    def speaker(self, _):
        sp.Popen('python chat.py speaker', shell=True)

    @rumps.clicked("识图")
    def analysis(self, _):
        pipe = sp.Popen('python sc.py',shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        # output,error=pipe.communicate()
        if pipe.returncode == 0:
            sp.Popen('python ocr.py &&',shell=True)

    # @rumps.clicked("聊天","虚拟恋人")
    # def lover(self, _):
    #     sp.Popen('python chat.py lover', shell=True)

    # @rumps.clicked("聊天","心理咨询")
    # def psychological(self, _):
    #     sp.Popen('python chat.py psychological', shell=True)

    # @rumps.clicked("聊天","法律顾问")
    # def lawyer(self, _):
    #     sp.Popen('python chat.py lawyer', shell=True)

    # @rumps.clicked("识图", "分析总结")
    # def analysis(self, _):
    #     sp.Popen(['python','sc.py'])

    # @rumps.clicked("识图", "文本摘要")
    # def summary(self, _):
    #     sp.Popen(['python','sc.py'])

    # @rumps.clicked("识图", "数据分类")
    # def dataclassification(self, _):
    #     sp.Popen(['python','sc.py'])

    # @rumps.clicked("识图", "代码审计")
    # def codereview(self, _):
    #     sp.Popen(['python','sc.py'])

    # @rumps.clicked("识图", "中文翻译")
    # def translator(self, _):
    #     sp.Popen(['python','sc.py'])

if __name__ == "__main__":
    OAI().run()