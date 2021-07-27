import os

cPath = os.getcwd()
lang = "ITA_M"


wavs = []
files = os.listdir(lang)
for i in files:
    if i.split(".")[-1] == "wav":
        wavs.append(i)

os.chdir("ITA_M")

for j in range(len(wavs)):
    os.rename(wavs[j], "%s_%03d.wav"%("ITA", j))
