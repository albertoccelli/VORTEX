# For development purposes only
import os

import numpy as np
from transliterate import translit
from scipy.io.wavfile import read, write

def capitalize(string):
    """
    Capitalizes only the first letter of a string. Does not change the others.
    """
    newstring = string[0].capitalize() + string[1:]
    return newstring


def make_commands(language, filename, transliteration=False, option="harman"):
    """
    For development purposes only.
    Reads a txt list of commands and divides them among the test cases.

    Only txt files from Harman database are currently supported.
    """
    # full list of commands (without repetition)
    command_list = []
    # list of commands including "PTT"
    commands_full = []
    # dictionary containing the command id associated to the command
    c_id = {}

    # build the command list (for HARMAN commands only - DEFAULT)
    if option == "harman":
        with open(filename, encoding="utf-8") as f:
            tests = 0
            code = 0
            issues = []
            for line in f.readlines():
                if "1." in line:
                    if len(issues) > 0:
                        commands_full.append(issues)
                        issues = []
                    tests += 1
                if "PTT" in line:
                    issues.append("000\tPTT\n")
                if language in line:
                    command = capitalize(
                        line.split(":")[-1].split(">>")[-1].split("Say")[-1].replace('"', '').replace(".", "").replace(
                            " ,", ",").replace(",", ", ").replace("  ", " ").replace("  ",
                                                                                     " ").lstrip().rstrip()) + "\n"
                    if transliteration:
                        command = command.replace("\n", "") + "\t" + translit(command, 'ru', reversed=True)
                    if command not in command_list:
                        code += 1
                        c_id[command] = "%03d" % code
                        command_list.append(command)
                        issues.append(c_id[command] + "\t" + command)
                    else:
                        issues.append(c_id[command] + "\t" + command)
            commands_full.append(issues)
    print("LANG: %s" % language)
    print("Number of tests: %s" % len(commands_full))
    print("Number of recorded commands: %s\n" % len(command_list))
    return commands_full, c_id


def playlist_from_commands(comms):
    """
    For development purposes only: creates a playlist with all the recorded audio files in the order
    they should be played.
    """
    playlist = []
    for i in range(len(comms)):
        for j in range(len(comms[i])):
            command = comms[i][j]
            if "PTT" not in command:
                playlist.append(command)
    return playlist


def write_to_files(comms, language):
    """
    For development purposes only: writes playlist and commands into a txt file.
    Use it to check the integrity of the commands.
    """
    playlist = playlist_from_commands(comms)
    playlist_nr = []
    playlist_nr_trad = []
    for p in playlist:
        if p.split("=>")[0] not in playlist_nr:
            playlist_nr.append(p.split("=>")[0])
            playlist_nr_trad.append(p)

    with open("../lists/%s_commands.txt" % language, "w", encoding="utf-16") as o:
        for p in playlist_nr_trad:
            o.write(p)
            # o.write(c.split(":")[-1].replace('"', ''))
    with open("../lists/s_playlist.txt" % language, "w", encoding="utf-16") as o:
        for p in playlist:
            o.write(p)
            # o.write(c.split(":")[-1].replace('"', ''))
    return


def translate(language, test_dict):
    """
    For development purposes only.
    Appends to the command its relative english (USA) command to check its significance.

    Example:
    >>> tradDictionary = translate("GED", test_dict)
    """
    b_lang = "ENU"
    try:
        for i in range(len(test_dict[language])):
            for j in range(len(test_dict[language][i])):
                # check whether the string has already been translated
                if len(test_dict[language][i][j].split("=>")) == 1 and "PTT" not in test_dict[language][i][j]:  #
                    test_dict[language][i][j] = (
                            test_dict[language][i][j].replace("\n", "\t") + "=> %s" %
                            test_dict[b_lang][i][j].split("\t")[1])
    except:
        pass
    return test_dict


def read_preconditions(filename="to_separe.txt"):
    """
    For development purposes only: read the preconditions for each voice recognition test.
    """
    prec = []
    with open(filename, "r", encoding="utf-8") as f:
        multline = False
        line = []
        for ln in f.readlines():
            if '"' in ln:
                if not multline:
                    multline = True
                    line.append(ln.replace('"', ''))
                else:
                    multline = False
                    line.append(ln.replace('"', ''))
                    prec.append("".join(line))
                    line = []
            elif multline:
                line.append(ln.replace('"', ''))
            elif not multline:
                prec.append(ln)
    for p in prec:
        p.replace("\n", "")
    return prec

def cut_pauses(audio_file, treshold = 100, out_file = None):
    fs, audio_data = read(audio_file)
    # cut silence at the beginning and at the end
    for i in range(len(audio_data)):
        if abs(audio_data[1]) > treshold and abs(audio_data[-1]) > treshold:
            break
        else:
            if abs(audio_data[1]) < treshold:
                audio_data = audio_data[1:]
            if abs(audio_data[-1]) < treshold:
                audio_data = audio_data[:-1]
    if out_file == None:
        out_file = audio_file
    write(out_file, fs, audio_data.astype(np.int16))
    return

if __name__ == "__main__":
    from configure import load_list, save_list

    folder = "../phrases/harman/PTP/"
    '''
    files = [(folder + i) for i in os.listdir(folder) if i[-4:] == ".wav"]
    for i in range(len(files)):
        print("Progress: %0.2f" % (100*((i+1)/len(files))))
        cut_pauses(files[i], treshold=80)
    '''
    # load test file
    print("Loading configuration file\n")
    test = load_list()

    '''
    # read new commands from list
    test = oldtest

    # select new language to add
    
    lang = "PTP"
    test[lang] = []  # resets command list to avoid conflicts
    commands, cid = make_commands(lang, "to_separe.txt", transliteration=False)
    test[lang] = commands

    read_preconditions()
    # write_to_files(test[lang], lang)
    print(test["preconditions"])
    input("Press ENTER to save preconditions")
    save_list(test)
    '''
