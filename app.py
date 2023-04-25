import rumps
import subprocess

class OAI(rumps.App):
    def __init__(self):
        super(OAI, self).__init__("AIBOT", icon="icon.png")   

    @rumps.clicked("聊天","模拟面试")
    def interview(self, _):
        # subprocess.call is blocking but Popen is Non-Blocking
        subprocess.Popen('python chat.py interview', shell=True)

    @rumps.clicked("聊天","口语聊天")
    def speaker(self, _):
        # subprocess.call(['python','chat.py','speaker'])
        subprocess.Popen('python chat.py speaker', shell=True)

    @rumps.clicked("识图")
    def takescreenshot(self, _):
        subprocess.Popen(['python','sc.py'])

if __name__ == "__main__":
    OAI().run()