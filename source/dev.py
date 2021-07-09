# For development purposes only

from transliterate import translit


def Capitalize(string):
    '''
    Capitalizes only the first letter of a string. Does not change the others.
    '''
    newstring = string[0].capitalize()+string[1:]
    return newstring


def make_commands(lang, filename, transliteration = False, option = "harman"):
    '''
    For development purposes only.
    Reads a txt list of commands and divides them among the test cases.

    Only txt files from Harman database are currently supported.
    '''
    #full list of commands (without repetition)
    commandList = []
    #list of commands including "PTT"
    commands = []
    #dictionary containing the command id associated to the command
    cID = {}

    # build the command list (for HARMAN commands only - DEFAULT)
    if option == "harman":
        with open(filename, encoding = "utf-8") as f:
            tests = 0
            code = 0
            issues = []
            for line in f.readlines():
                if "1." in line:
                    if len(issues) > 0:
                        commands.append(issues)
                        issues = []
                    tests+=1
                if "PTT" in line:
                    issues.append("000\tPTT\n")
                if lang in line:
                    command = Capitalize(line.split(":")[-1].split(">>")[-1].split("Say")[-1].replace('"','').replace(".","").replace(" ,",",").replace(",",", ").replace("  "," ").replace("  "," ").lstrip().rstrip())+"\n"
                    if transliteration:
                        command = command.replace("\n", "") + "\t" + translit(command, 'ru', reversed=True)
                    if command not in commandList:
                        code+=1
                        cID[command] = "%03d"%code
                        commandList.append(command)
                        issues.append(cID[command]+"\t"+command)
                    else:
                        issues.append(cID[command]+"\t"+command)
            commands.append(issues)    
    print("LANG: %s"%lang)
    print("Number of tests: %s"%len(commands))
    print("Number of recorded commands: %s\n"%len(commandList))
    return commands, cID


def playlistFromCommands(commands):
    '''
    For development purposes only: creates a playlist with all the recorded audio files in the order
    they should be played.
    '''
    playlist = []
    for i in range(len(commands)):
        for j in range(len(commands[i])):
            command = commands[i][j]
            if "PTT" not in command:
                playlist.append(command)
    return playlist


def writeToFiles(commands, lang):
    '''
    For development purposes only: writes playlist and commands into a txt file.
    Use it to check the integrity of the commands.
    '''
    playlist = playlistFromCommands(commands)
    playlistNR = []
    playlistNRTrad = []
    for p in playlist:
        if p.split("=>")[0] not in playlistNR:
            playlistNR.append(p.split("=>")[0])
            playlistNRTrad.append(p)
            
    with open("../lists/%s_commands.txt"%lang, "w", encoding = "utf-16") as o:
        for p in playlistNRTrad:
            o.write(p)
            #o.write(c.split(":")[-1].replace('"', ''))
    with open("%../lists/s_playlist.txt"%lang, "w", encoding = "utf-16") as o:
        for p in playlist:
            o.write(p)
            #o.write(c.split(":")[-1].replace('"', ''))
    return


def translate(lang, test, undo = False):
    '''
    For development purposes only.
    Appends to the command its relative english (USA) command to check its significance.

    Example:
    >>> tradDictionary = translate("GED", dictionary)

    To remove the traduction, just make sure the "undo"testloop.py
    '''
    bLang = "ENU"
    try:
        for i in range(len(test[lang])):
            for j in range(len(test[lang][i])):
                if len(test[lang][i][j].split("=>")) == 1 and "PTT" not in test[lang][i][j]: #check whether the string has already been translated
                    test[lang][i][j] = (test[lang][i][j].replace("\n", "\t") + "=> %s"%test[bLang][i][j].split("\t")[1])
    except:
        pass
    return test
                    

def readPreconditions(filename = "to_separe.txt"):
    '''
    For development purposes only: read the preconditions for each voice recognition test.
    '''
    prec = []
    with open(filename, "r", encoding = "utf-8") as f:
        multline = False
        line = []
        for l in f.readlines():
            if '"' in l:
                if multline == False:
                    multline = True
                    line.append(l.replace('"', ''))
                else:
                    multline= False
                    line.append(l.replace('"', ''))
                    prec.append("".join(line))
                    line = []
            elif multline:
                line.append(l.replace('"', ''))
            elif not multline:
                prec.append(l)
    for p in prec:
        p = p.replace("\n","")
    return prec
  
    

if __name__ == "__main__":
    
    from configure import loadList, saveList
    
    #load test file
    print("Loading configuration file\n")
    oldtest = loadList()
 
    #read new commands from list
    test = oldtest
    '''
    #select new language to add
    lang = "ITA"
    test[lang] = [] # resets command list to avoid conflicts
    commands, cid = make_commands(lang, "../lists/to_separe.txt", transliteration = False)
    test[lang] = commands
 

    #writeToFiles(test[lang], lang)
    saveList(test)
    saveList(test, exp = False)
    '''
