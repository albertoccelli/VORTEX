import os

cPath = os.getcwd()
lang = "FRF"


wavs = []
files = os.listdir(lang)
for i in files:
    if i.split(".")[-1] == "wav":
        wavs.append(i)

os.chdir("FRF")

for j in range(len(wavs)):
    os.rename(wavs[j], "%s_%03d.wav"%("FRF", j))
