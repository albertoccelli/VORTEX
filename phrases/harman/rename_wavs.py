import os

cPath = os.getcwd()
lang = "PLP"


wavs = []
files = os.listdir(lang)
for i in files:
    if i.split(".")[-1] == "wav" and i[:3] == lang:
        wavs.append(i)

os.chdir(lang)

for j in range(len(wavs)):
    os.rename(wavs[j], "%s_%03d.wav"%(lang, j))
