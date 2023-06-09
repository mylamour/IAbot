import io
import spacy
import sys
from markdown import markdown
import pytesseract
from PIL import Image
from cnocr import CnOcr
from pypdf import PdfReader
from prompts import Prompt
from core import OCR_LANG, OCR_TYPE, brain
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextBrowser
class OCR():
    def __init__(self) -> None:
        if OCR_LANG == "zh-CN":
            self.spacy_model = "zh_core_web_sm"
            self.rec_model = 'ch_PP-OCRv3'

        if OCR_LANG == "en-US":
            self.spacy_model = "en_core_web_sm"
            self.rec_model = 'en_PP-OCRv3'
        self.nlp = spacy.load(self.spacy_model)
        self.img_file = None
        self.ocr_type = OCR_TYPE
    
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
            out = self.paddOCR(self.rec_model)

        self.doc = self.nlp(out)
        sentences = [sent.text for sent in self.doc.sents]  
        return sentences

    def tessOCR(self, lang='eng+chi_sim'):
        out = pytesseract.image_to_string(self.img_file, lang)
        return out

    def paddOCR(self, rec_model_name):
        ocr = CnOcr(rec_model_name)
        out = "".join([i['text'] for i in ocr.ocr(self.img_file)])
        return out
    

if __name__ == "__main__":
    rco = OCR()
    res = "".join(rco.ocr_img('.latest.screenshot.png'))
    conversation = []
    conversation.append(Prompt.screenshot.value)
    conversation.append({
        "role": "user",
        "content": res
    })
    result = brain(conversation)
    app = QApplication(sys.argv)
    window = QMainWindow()
    text_browser = QTextBrowser(window)
    window.setCentralWidget(text_browser)
    window.setGeometry(QApplication.primaryScreen().size().width(), 0, 400, QApplication.primaryScreen().size().height())
    text_browser.setText(markdown(result))
    window.show()
    sys.exit(app.exec())