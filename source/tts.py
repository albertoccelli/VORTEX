#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------
#
# Name:             albertts.py
#
# Author: 	    Alberto Occelli
#		    albertoccelli@gmail.com
#		    a.occelli@reply.it
#	            occellialberto@telematicainformatica.it
#
# Version: 	    2.0.1
#
# Creation: 	    01/04/2021
#
# Last updated:     03/06/2021
#
# Changelog:	    1.0.0 - created
#                   1.2.0 - automatically detects txt files
#                   1.2.1 - code optimization
#                   1.3.0 - module introduction
#                   1.4.0 - extended flexibility in reading the txt
#                   1.8.0 - OOP introduced
#                   2.0.0 - configuration file added
#                   2.0.1 - save to WAV
#
# Description:      this program utilizes the Google Cloud API for the TTS, in order to convert text file
#                   into WAV files. Suitable for FCA test norm LP.7Z027.
#
# Known issues:     after quite some requests, the TTS API overflows. You have to wait a couple of ours before
#                   resuming.
#
# Dependencies:     gTTS
#
#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------

from gtts import gTTS
import csv
import subprocess
import os.path
#import re
import shutil
from datetime import datetime
from pydub import AudioSegment
from tempfile import TemporaryFile
from . play import play_wav, play_data


# conventional language code {CODE: [LANGUAGE, ACCENT]}
code = {"ARW": ["ar", "com"],
        "CHC": ["zh", "zh"],
        "DUN": ["nl", "nl"],
        "ENG": ["en", "com.uk"],
        "ENA": ["en", "com.au"],
        "ENI": ["en", "com.in"],
        "ENU": ["en", "us"],
        "FRF": ["fr", "fr"],
        "FRF": ["fr", "ca"],
        "GED": ["de", "de"],
        "ITA": ["it", "it"],
        "JPJ": ["ja", "com"],
        "KRK": ["ko", "com"],
        "PLP": ["pl", "pl"],
        "PTP": ["pt", "pt"],
        "PTB": ["pt", "com.br"],
        "RUR": ["ru", "ru"],
        "SPE": ["es", "es"],
        "SPM": ["es", "com.mx"],
        "TRT": ["tr", "com"]
        }

def say(text, language = "it", accent = "it", engine = "google", save = True, file=None, talk = False):
    """
    Simply produces a wav from a txt.
    Just put a text, the file name, the language code and the accent code.

    ========================================
    | LANGUAGE   | LANG CODE | ACCENT CODE |
    ----------------------------------------
      Arabic     |   ar      |   com
      Chinese    |   zh      |   zh
      Dutch      |   nl      |   nl
      English    |   en      |   com.uk 
                 |   "       |   com.au
                 |   "       |   com.in
                 |   "       |   us
      French     |   fr      |   fr
                 |   "       |   ca
      German     |   de      |   de
      Italian    |   it      |   it
      Japanese   |   ja      |   com
      Korean     |   ko      |   com
      Polish     |   pl      |   pl
      Portuguese |   pt      |   pt
                 |   "       |   com.br
      Russian    |   ru      |   ru
      Spanish    |   es      |   es
                 |   "       |   com.mx
      Turkish    |   tr      |   com
    ========================================
    """
    if len(language)>2:
        l = language
        language = code[l][0]
        accent = code[l][1]   
    
    if engine == "google":
        tts = gTTS(text=text, lang=language, tld=accent)
        if file==None:
            file = "%s.wav"%(text)
        tts.save("temp.mp3")                        # Save command file to mp3
        print("Converting from mp3 to wav")
        sound =  AudioSegment.from_mp3("temp.mp3")  # convert from mp3 to wav
        sound.export(file, format = "wav")
        if talk:
            play_wav(file)
        if not save:
            os.remove(file)
        os.remove("temp.mp3")
        
    return tts
 

if __name__ == "__main__":

    say("Ciao")
