#!/usr/bin/env python3
import os
import time
import speech_recognition as sr         #only with wit.ai
from deep_translator import GoogleTranslator
import requests
import json

WIT_AI_KEY = "F7MGCUYFA7QY7NRGTMOCB6SH25HT7P3X"

# dictionary containing the tokens for all the supported languages
languages = {   "en": "76HKENBCTDTG4SM2WFLAB2PA37AICVX5",   # ENG
                "it": "OGNMHLE35IAKHWA7UUJYHRCEWTQGCBXS",   # ITA
                "es": "OSJ24LNG46WFNFXOHXSCNTN2KLQOL3FU",   # ESP
                "fr": "IGBVPMRVWDYUA7D3N7YXZTJCTHK5ILC4",   # FRA
                "pl": "P3MSP2MSKGFWODINR5E6G7FG4UZVEZGO",   # AR
                "ru": "M4XJV6YM3X6RFOWLIPDNFXFQCPVXVHDP",   # AR
                "ar": "6M2LBQS6JKGV7EQPWV4I3DKEIEHYGO7N"    # AR
}


def recognize(filename = "output.wav", source = "it", target = "en"):
    
    WIT_AI_KEY = languages.get(source)
    print("---------------------------------------------------")
    print("Detecting audio (language: %s)...\n"%source)
    print("Token: %s\n"%WIT_AI_KEY)
     
    AUDIO_FILE = filename # can recognize: .aiff .flac .wav

    API_ENDPOINT = "https://api.wit.ai/speech"
    ACCESS_TOKEN = WIT_AI_KEY

    with open(AUDIO_FILE, "rb") as f:
        audio = f.read()

    headers = {'authorization': 'Bearer '+ACCESS_TOKEN, 'Content-Type': 'audio/wav'}
    resp = requests.post(API_ENDPOINT, headers = headers, data = audio)
    data = json.loads(resp.content)
    phrase = data.get('text')
    intent = data.get('intent')
    
    if phrase == "":
        print("Nothing to translate here :(")
    else:
        print("- Received response: \t%s (%s)"%(phrase.capitalize(), intent))
        translated = GoogleTranslator(source = source, target = "en").translate(phrase)
        print("- Translation: \t\t%s" %translated)
    print("---------------------------------------------------")
    return phrase, intent


        
if __name__ == "__main__":

    txt = recognize("test.wav")
