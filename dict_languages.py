from bs4 import BeautifulSoup
import lxml
import requests
import gtts

response = requests.get('http://espeak.sourceforge.net/languages.html')
yc_webpage = response.text
soup = BeautifulSoup(yc_webpage, 'lxml')
languages = soup.select(selector='dt strong')
languages = [language.getText().replace('\xa0', '') for language in languages][5:]
espeak_languages_dict = {}
for language in languages:
    code = language.split(' ')[0]
    language1 = language.split(' ')[1]
    espeak_languages_dict[code] = language1
gTTS_languages_dict = gtts.tts.tts_langs()
espeak_with_gTTS = {**espeak_languages_dict, **gTTS_languages_dict}
if 'zh' in espeak_languages_dict:
    espeak_languages_dict.pop('zh')
if 'ru' in espeak_languages_dict:
    espeak_languages_dict.pop('ru')
if 'zh-yue' in espeak_languages_dict:
    espeak_languages_dict.pop('zh-yue')
espeak_with_gTTS_keys = sorted(espeak_with_gTTS, key=espeak_with_gTTS.get)
espeak_with_gTTS_sorted = {}
for i in espeak_with_gTTS_keys:
    espeak_with_gTTS_sorted[i] = espeak_with_gTTS[i]

languages = [f'{espeak_with_gTTS[key]} - {key}' for key in espeak_with_gTTS_sorted]
