# Intro

<video controls style="display: block; margin: auto;">
  <source src="https://user-images.githubusercontent.com/12653147/234508201-e01a9d3e-3784-42f8-a0d4-0f5789f0db3e.mp4" type="video/mp4">
</video>

# Requirements

![image](https://user-images.githubusercontent.com/12653147/234492515-66a9aad7-3c3f-4e32-a531-e4bb71a8d014.png)

* Chat(OpenAI powered by azure cognitive services)
* Speech(powered by azure cognitive services)
* OCR by cnOCR (powerd by paddlepaddleOCR)

for localhost solution, speech to text and text to speech can be instead by:
* Bark(Text to Speech)
* Whisper(Speech to Text)

# Quickstart

```bash
virtualenv --python=python3.10 lenv
pip install -r requirement
```

Edit your template file and replace api keys & models

```bash
cp .env.template .env
python app.py
```