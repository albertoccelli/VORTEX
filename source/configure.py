def save_list(test, filename="../database/r1h.vrtl", exp=True):
    """
    Saves the dictionary containing the commands information into a special file (.vrtl) to be imported
    in a second time.
    """
    languages = []
    for i in test.keys():
        languages.append(i)
    if not exp:
        with open("config.vrtl", "w", encoding="utf-16") as c:
            for lang in languages:
                print("Writing %s" % lang)
                c.write("@%s\n" % lang)
                for i in range(len(test[lang])):
                    c.write("\t@%03d\n" % (i + 1))
                    for j in range(len(test[lang][i])):
                        c.write("\t" + test[lang][i][j])
            c.write("\n")
    else:
        with open(filename, "w", encoding="utf-16") as c:
            c.write(str(test))

    return languages


def load_list(filename="../database/r1h.vrtl"):
    """
    Imports the commands information from the .vrtl file and creates a dictionary suitable for the tests.
    """
    if __name__ == "__main__":
        print("Reading playlist information from file %s..." % filename, end='')
    test = {}
    try:
        with open(filename, "r", encoding="utf-16") as p:
            for line in p.readlines():
                test = eval(line)
    except FileNotFoundError:
        print("\nConfiguration file not found!")
    return test
