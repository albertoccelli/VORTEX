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
from os import listdir
import os.path
#import re
import shutil
from datetime import datetime
from pydub import AudioSegment
from tempfile import TemporaryFile
from .play import playWav, playData

class Talker():
    """
    Defines a new fancy object: the TALKER. Each talker can speak up to 20 languages:
    Arabic, Chinese, Dutch, English (Australia), English (India), English (UK),
    English (US), French (France), French (Canada), German, Italian, Japanese,
    Korean, Polish, Portuguese (Brazil), Portuguese (Portugal), Russian, Spanish (Mexico),
    Spanish (Spain), Turkish.

    For each language, a list of commands can be defined and filled with the
    readTxt() method.
    """
    eng = [] 
    enu = []
    spm = []
    frc = []
    ged = []
    ita = []
    frf = []
    spe = []
    ptp = []
    dun = []
    plp = []
    trt = []
    rur = []
    ptb = []
    eni = []
    ena = []
    arw = []
    krk = []
    jpj = []
    chc = []
    
    lang = {
            "commands"   : [arw,   chc,  dun,  ena,  eni,  eng,  enu,  frf,  frc,  ged,  ita,  jpj,  krk,  plp,  ptb,  ptp,  rur,  spm,  spe,trt],
            "enable"     : [0,     0,    0,    0,    0,    1,    1,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,0 ], 
            "lang"       : ["ar",  "zh", "nl", "en", "en", "en", "en", "fr", "fr", "de", "it", "ja", "ko", "pl", "pt", "pt", "ru", "es", "es", "tr"],
            "accent"     : ["com", "zh", "nl", "com.au", "co.in", "co.uk", "us", "fr", "ca", "de", "it", "com", "com", "pl", "com.br", "pt", "ru",
                            "com.mx", "es", "com"],
            "description": ["Arabic", "Chinese", "Dutch", "English(Australia)", "English(India)", "English(UK)", "English(US)", "French(France)",
                            "French(Canada)", "German", "Italian", "Japanese", "Korean", "Polish", "Portuguese(Brazil)", "Portuguese(Portugal)",
                            "Russian", "Spanish(Mexico)", "Spanish(Spain)", "Turkish"]  
        }


    def __init__(self, name):
        self.created = (datetime.now()).strftime("%Y_%m_%d_%H_%M_%S")   # detects current time
        self.name = name                                                # name of the talker
        self.tFile = "config_%s.tlk"%name                               # config filename
        self.issaved = self.tFile in os.listdir()                       # checks if a config file is already in the working directory
        if not self.issaved:
            print("Configuration file not found. Creating new...")
            f = open(self.tFile, "w")
            f.close()
            self.saveConf()
        #load configuration
        else:
            print("Loading configuration...")
        self.conf = []
        with open(self.tFile, "r") as f:
            for l in f.readlines():
                l=l.split("@")[0]
                if len(l)>0 and l!="\n":
                    self.conf.append(l)
        for i in range(len(self.conf)):
            #enabled languages
            if i < len(self.lang.get("enable")):
                self.lang.get("enable")[i]=int(self.conf[i][0])
        print("\n")
        

    def saveConf(self, file = None):
        """
        Save current configuration into a .tlk file. This is saved by default into
        the current working directory, otherwise you should include it as a function
        argument
        """
        if file == None:
            file = self.tFile
        self.issaved = file in os.listdir()
        if not self.issaved:
            print("Creating configuration file (%s)"%file)
            f = open(file, "w")
            f.close()
        #enabled languages
        elif self.issaved:
            print("Saving configuration file (%s)"%file)
        tbw = []
        tbw.append("@LAST SAVED: %s"%self.created)
        tbw.append("@ENABLED LANGUAGES:")
        for i in range(len(self.lang.get("enable"))):
            tbw.append("%s @ %s"%(self.lang.get("enable")[i],self.lang.get("description")[i]))    
        with open(file, "w") as f:
            for l in tbw:
                f.write(l)
                f.write("\n")       


    def deleteConf(self):
        """
        Delete configuration file of enabled languages.
        """
        print("Deleting configuration file (%s)"%file)
        os.remove(self.tFile)


    def loadConf(self, file = None):
        """
        Load configuration file of enabled languages. The file, in the format .tlk,
        should be in the working directory, but can also be specified as a function
        argument
        """
        try:
            if file == None:
                file = self.tFile
            print("Loading configuration file")
            self.conf = []
            with open(file, "r") as f:
                lines = f.readlines()
                if lines[0][0:9] == "@CONFFILE":
                    for l in lines:
                        l=l.split("@")[0]
                        if len(l)>0 and l!="\n":
                            self.conf.append(l)
                else:
                    print("Configuration file corrupted!: %s"%lines[0][0:9])
                    return 0
            
            for i in range(len(self.conf)):
                #enabled languages
                if i < 20:
                    print("%s     %s"%(self.conf[i][0], self.lang.get("description")[i]))
                    self.lang.get("enable")[i]=int(self.conf[i][0])
            print("\n")
            return file
        except FileNotFoundError:
            print("Configuration file not found!")
            return
        
        
    def knownLanguages(self, numbers = False):
        """
        This function returns the list of the current enabled languages of the talker.
        If the numbers=True argument is given, a list of the indexes of the known
        languages is given instead
        """
        kl = []
        kln = []
        for i in range(len(self.lang.get("commands"))):
            if self.lang.get("enable")[i] == 1:
                kl.append(self.lang.get("description")[i])
                kln.append(i)
        if numbers:
            return kln
        else:
            return kl


    def enable(self, language = None):
        """
        This function enables or disables one of the languages of the talker.
        
        Argument: integer
        
        0  - Arabic
        1  - Chinese
        2  - Dutch
        3  - English (Australia)
        4  - English (India)
        5  - English (UK)
        6  - English (US)
        7  - French (France)
        8  - French (Canada)
        9  - German
        10 - Italian
        11 - Japanese
        12 - Korean
        13 - Polish
        14 - Portuguese (Brazil)
        15 - Portuguese (Portugal)
        16 - Russian
        17 - Spanish (Mexico)
        18 - Spanish (Spain)
        19 - Turkish

        If no argument is given, the list of the current known languages is printed
        """
        if language == None:
            return self.knownLanguages()
        while True:
            try:
                if type(language) == list:
                    en = []
                    for i in range(len(language)):
                        self.lang.get("enable")[language[i]] = abs(self.lang.get("enable")[language[i]] - 1)
                        en.append(self.lang.get("enable")[language[i]])
                        print("%s: %d"%(self.lang.get("description")[language[i]], self.lang.get("enable")[language[i]]))
                    return en
                elif type(language) == int:
                    self.lang.get("enable")[language] = abs(self.lang.get("enable")[language] - 1)
                    print("%s: %d"%(self.lang.get("description")[language], self.lang.get("enable")[language]))
                    return self.lang.get("enable")[language]
            except IndexError:
                language=int(input("Invalid number. Argument must be from 0 to %d. Please choose again: "%len(self.lang.get("enable"))))


    def isEnabled(self, language):
        return self.lang.get("enable")[language]

    
    #Talker learns list of commands
    def learn(self, cFile, verbose = False):
        """
        Function to read a txt list containing all the commands you want to test.
        The list should contain commands in the following format:
        ENU: 0command
        ITA: comando
        etc...
        """
        with open(cFile, encoding='utf-8') as txt:
            print("Reading command list...")
            rows = txt.readlines()
            for row in rows:
                # Correct text ("Harman files")
                row = row.replace('"', '')
                row = row.replace('\n', '')
                row = row.replace('<ContactName>', contact)
                row = row.replace(': Say', '>> Say :')
                row = row.replace("-->", ">> Say:")
                if row != "":
                    if True:                    
                        sRow = row.split(". ")              #eliminate numbers at the beginning
                        langCode = sRow[-1][0:3]            #isolate the language code
                        command = sRow[-1].split(":")[-1]
                        command = command.split("/")[0]
                        command = command.replace(">", "")
                        command = command.replace("<", "")
                        command = command.replace(" AM", " A M") 
                        command = command.replace(" FM", " F M") 
                        command = command.replace("\t", "") 
                        command = command.replace("contactname", "John")
                        if verbose:
                            print("%s: %s"%(langCode, command))
                        if (langCode).upper() == "ENU":
                            self.enu.append(command)
                        elif (langCode).upper() == "ENG":
                            self.eng.append(command)
                        elif (langCode).upper() == "SPM":
                            self.spm.append(command)
                        elif (langCode).upper() == "FRC":
                            self.frc.append(command)
                        elif (langCode).upper() == "GED":
                            self.ged.append(command)
                        elif (langCode).upper() == "ITA" or langCode == "ITI":
                            self.ita.append(command)
                        elif (langCode).upper() == "FRF":
                            self.frf.append(command)
                        elif (langCode).upper() == "SPE":
                            self.spe.append(command)
                        elif (langCode).upper() == "PTP":
                            self.ptp.append(command)
                        elif (langCode).upper() == "PTP":
                            self.ptp.append(command)
                        elif (langCode).upper() == "DUN":
                            self.dun.append(command)
                        elif (langCode).upper() == "PLP":
                            self.plp.append(command)
                        elif (langCode).upper() == "TRT":
                            command = command.replace("song name", "kuzu kuzu")
                            command = command.replace("album name", "karma")
                            command = command.replace("artist name", "tarkan")
                            self.trt.append(command)
                        elif (langCode).upper() == "RUR":
                            command = command.replace("genre name", genre)
                            self.rur.append(command)
                        elif (langCode).upper() == "PTB":
                            self.ptb.append(command)
                        elif (langCode).upper() == "ENI":
                            self.eni.append(command)
                        elif (langCode).upper() == "ENA":
                            self.ena.append(command)
                        elif (langCode).upper() == "ARW":
                            self.arw.append(command)
                        elif (langCode).upper() == "KRK":
                            self.krk.append(command)
                        elif (langCode).upper() == "JPJ":
                            self.jpj.append(command)
                        elif (langCode).upper() == "CHC":
                            self.chc.append(row[-1])
            print("...done!\n")
            return
        

    # Talker speaks, saving wave files
    def talk(self, folder, verbose = True, language=lang.get("lang"), accent=lang.get("accent"), commands=lang.get("commands"), enable=lang.get("enable")):
        """
        Save each command in a WAV file, by using the gTTS API (Google cloud).
        If the verbose argument is given, each command is also printed to the terminal.

        The folder is created in the working path by default.
        """
        nLanguages = 0
        for i in range(len(self.lang.get("enable"))):
            if self.lang.get("enable")[i] == 1:
                nLanguages += 1
        while True:
            try:
                os.mkdir(folder)
                break
            except FileExistsError:
                folder = input("Folder "+folder+" already exists. Please choose another name")
        error = False
        pCommand = ""
        current = 0
        for i in range(len(language)):
            if enable[i] == 1:
                current += 1
                print("Language: %s"%(self.lang.get("description")[i]))
                if len(commands[i])>0:
                    while True:
                        try:
                            os.mkdir(folder+"/"+self.lang.get("description")[i]) # Create language folder
                            for j in range(len(commands[i])):
                                try:
                                    if len(commands[i][j])>0 and commands[i][j] != pCommand and commands[i][j] != " ":
                                        filename = folder+"/"+self.lang.get("description")[i]+'/'+language[i]+'_'+accent[i]+"_"+str(j+1).zfill(3)+"_"+commands[i][j].replace("?", "")+'.wav'
                                        tts = gTTS(text=commands[i][j], lang=language[i], tld=accent[i])
                                        tts.save("temp.mp3")                        # Save command file as temporary mp3 file
                                        sound =  AudioSegment.from_mp3("temp.mp3")  # convert from mp3 to wav
                                        sound.export(filename, format = "wav")
                                        os.remove("temp.mp3")
                                        if verbose:
                                            print(str(1+j)+"/"+str(len(commands[i]))+": "+commands[i][j])
                                        pCommand = commands[i][j]
                                except KeyboardInterrupt:
                                    print("Aborting generation")
                                    break
                            break
                        except KeyboardInterrupt:
                            print("Aborting generation")
                            break
                        except SyntaxError:
                            print("Error with the Google API. Please try later or check your internet connection")
                            input()
                            error = True
                            break
                    print(str((current/nLanguages)*100)+"% completed...\n")
        # The end
        if not error:
            input("\nDone! Enjoy your voices :D\n\n(press ENTER to quit...)")

    
# default values to substitute to commands
song = "hey nineteen"
album = "gaucho"
artist = "steely dan"
genre = "rock"
contact = "Giovanni"


# Choose text files to read. Otherwise list all txt files
def txtDetect(choice = False):
    """
    Detects all the txt files contained in the current working folder.
    """
    files = []
    global cFile 
    cFile = "commands.txt"
    for i in range(len(os.listdir())):
        if os.listdir()[i][-4:] == ".txt":
            files.append(os.listdir()[i])
    if choice:
        if len(files) == 1:
            ch = input(files[0]+" found. Continue with it? (y/n)")
            if ch.lower() == "y":
                cFile = files[0]
            else:
                print("Ok, goodbye then")
                quit()
        elif len(files) > 1:
            print("Files found: \n")
            for i in range(len(files)):
                print("%s) "%(str(i+1),files[i]))
            ch = input("\nWhich one should I take? (1 to %d"%(len(files)))
            cFile = files[int(ch)-1]
        else:
            cFile = "commands.txt"
        print("\nContinuing with "+str(cFile)+".")
        input()
        return cFile;
    else: return files


def say(text, file=None, language = "it", accent = "it", engine = "google", save = True, talk = False):
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
    if engine == "google":
        if language != "it" and accent == "it":
            accent = "com"
        tts = gTTS(text=text, lang=language, tld=accent)
        if file==None:
            file = "%s.wav"%(text)
        tts.save("temp.mp3")                        # Save command file to mp3
        print("Converting from mp3 to wav")
        sound =  AudioSegment.from_mp3("temp.mp3")  # convert from mp3 to wav
        sound.export(file, format = "wav")
        if talk:
            playWav(file)
        if not save:
            os.remove(file)
        os.remove("temp.mp3")
        
    return tts                       

#def main():
    #txtDetect(choice = True)
    #decodeTxt(cFile)
    #listTalk(cFile)
    #commandsToTxt(lang)


def readTxt(file):
    with open(file) as txt:
        rows = txt.readlines()
        commands = []
        for i in rows:
            commands.append(i.split("Say:")[1].replace("\t","").replace("\n","").replace)
    return commands


if __name__ == "__main__":
    '''
    albert = Talker("albert")
    albert.learn(txtDetect()[0])  # talker learns command list
    albert.talk("OUTPUT")
    '''

    say("Ciao")
