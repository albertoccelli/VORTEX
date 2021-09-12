def make_commands(lang, filename):
    #full list of commands
    testsequence = []
    #list of commands without repetition
    commands = []
    #dictionary containing the command id associated to the command
    cID = {}

    with open(filename, encoding = "utf-8") as f:
        tests = 0
        code = 0
        for line in f.readlines():
            if "1." in line:
                tests+=1
            if lang in line :
                command = line.split(":")[-1].split("Say")[-1].replace('"','').replace(".","").replace(" ,",",").replace(",",", ").replace("  "," ").replace("  "," ").lstrip().capitalize()

                if command not in commands:
                    commands.append(command)
                    code+=1
                    cID[command] = "%03d"%code
                    testsequence.append(command)
                else:
                    testsequence.append(command)

    # define sequence of the audiofiles
    playlist = []
    for test in testsequence:
        playlist.append(cID[test])

    with open("commands_%s.txt"%lang, "w", encoding = "utf-8") as o:
        for c in commands:
            o.write(c)
            #o.write(c.split(":")[-1].replace('"', ''))
    with open("playlist_%s.txt"%lang, "w", encoding = "utf-8") as o:
        for p in playlist:
            o.write(p)
            #o.write(c.split(":")[-1].replace('"', ''))
            
    print("LANG: %s\n"%lang)
    print("Number of tests: %s"%tests)
    print("Number of commands: %s"%len(commands))
    print("Number of issues: %s\n"%len(testsequence))
    
    return commands, testsequence, playlist, tests


if __name__ == "__main__":
    
    langs = ["PLP"]
    commands = []
    testsequence = []
    playlists = []
    
    for l in langs:
        cmd, ts, pls, tests = make_commands(l)
        commands.append(cmd)
        testsequence.append(ts)
        playlists.append(pls)
