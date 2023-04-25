import io
import os
import wx
import cv2  
import time  
import spacy
import tempfile
import pyautogui
import pytesseract
import numpy as np
from mss import mss
from PIL import Image
from cnocr import CnOcr
from pypdf import PdfReader
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

OCR_TYPE = os.environ.get("OCR_TYPE")
OCR_LANG = os.environ.get("OCR_LANG")

if OCR_LANG == "zh-CN":
    spacy_model = "zh_core_web_sm"
    rec_model = 'ch_PP-OCRv3'

if OCR_LANG == "en-US":
    spacy_model = "en_core_web_sm"
    rec_model = 'en_PP-OCRv3'

class OCR():
    def __init__(self, ocr_type=OCR_TYPE) -> None:
        self.nlp = spacy.load(spacy_model)
        self.img_file = None
        self.ocr_type = ocr_type
        #  below code was design for super resolution then ocr 
        # rdn = RDN(weights='psnr-small')
        # sr_img = rdn.predict(lr_img)
        # new_img = Image.fromarray(sr_img)
    
    def ocr_pdf(self, pdf_file, page_number=None, scope=False):
        reader = PdfReader(pdf_file)
        outs = []
        pages = reader.pages

        if type(page_number) is int:
            pages = [reader.pages[page_number]]
        
        if type(page_number) is list:
            if scope:
                page_number = range(page_number[0],page_number[1])
            for page in page_number:
                for image_file_object in reader.pages[page].images:
                    self.img_file = Image.open(io.BytesIO(image_file_object.data))
                    outs.append(self.paddOCR())
            return "".join(outs)
            

        for page in pages:
            for image_file_object in page.images:
                self.img_file = Image.open(io.BytesIO(image_file_object.data))
                outs.append(self.paddOCR())
        return "".join(outs)

    def ocr_img(self,img_file):
        self.img_file = img_file
        if self.ocr_type == "tesseract":
            out = self.tessOCR()
        
        if self.ocr_type == "paddle":
            out = self.paddOCR()

        self.doc = self.nlp(out)
        sentences = [sent.text for sent in self.doc.sents]  
        return sentences

    def tessOCR(self, lang='eng+chi_sim'):
        out = pytesseract.image_to_string(self.img_file, lang)
        return out

    def paddOCR(self, rec_model_name=rec_model):
        ocr = CnOcr(rec_model_name=rec_model_name)
        out = "".join([i['text'] for i in ocr.ocr(self.img_file)])
        return out

class ScreenCapture(wx.App):  
    def OnInit(self):  
        self.frame = wx.Frame(None, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)  
        self.panel = wx.Panel(self.frame, wx.EXPAND)  
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)  
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)  
        self.panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)  
        self.panel.Bind(wx.EVT_MOTION, self.on_motion)  
  
        self.start_pos = None  
        self.end_pos = None  
        self.screen_rect = wx.GetDisplaySize()  
  
        self.frame.SetSize(self.screen_rect) 
        self.frame.Maximize(True)       #for full screen
        self.frame.SetTransparent(100)
        self.frame.Show()  
  
        return True  
  
    def on_paint(self, event):  
        if self.start_pos and self.end_pos:  
                    dc = wx.PaintDC(self.panel)  
                    dc.SetPen(wx.Pen(wx.RED, 2, wx.PENSTYLE_SOLID))  
                    dc.SetBrush(wx.Brush(wx.RED, wx.BRUSHSTYLE_TRANSPARENT))  
                    dc.DrawRectangle(self.start_pos[0], self.start_pos[1], self.end_pos[0] - self.start_pos[0], self.end_pos[1] - self.start_pos[1])

    def on_left_down(self, event):  
        self.start_pos = event.GetPosition()  
        self.end_pos = None  
        self.panel.CaptureMouse()  
  
    def on_left_up(self, event):  
        self.frame.Hide()
        if self.panel.HasCapture():  
            self.panel.ReleaseMouse()  
  
        if self.start_pos and self.end_pos:
            wx.CallLater(100, self.take_screenshot)  # if you take screnshot immeditaly, it will not work

    def take_screenshot(self):
        sc = pyautogui.screenshot(region=(
            self.start_pos[0], self.start_pos[1], self.end_pos[0] - self.start_pos[0], self.end_pos[1] - self.start_pos[1]))
        tmp_file = '.tmp.ocr.screentest.png'
        sc.save(tmp_file)
        self.ExitMainLoop()
  
    def on_motion(self, event):  
        if event.Dragging() and event.LeftIsDown():  
            self.end_pos = event.GetPosition()  
            self.panel.Refresh()

class ScreenRecord():
    def __init__(self) -> None:
        screen_size = (width, height) = (1920, 1080)  # Change this to your screen resolution  
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  
        out = cv2.VideoWriter('screen_recording.mp4', fourcc, 30.0, screen_size)  
        recording_time_limit = 10  # Record for 10 seconds  
        start_time = time.time()  
        with mss() as sct:  
            monitor = {'top': 0, 'left': 0, 'width': width, 'height': height}  
            while True:  
                img = np.array(sct.grab(monitor))  
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  
                out.write(frame)  
                if (time.time() - start_time) > recording_time_limit:  
                    break  
        out.release()