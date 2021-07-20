import os
from time import sleep


def print_square(string, title=None, margin=None, centering="left"):
    if margin is None:
        margin = [2, 2, 0, 0]
    strings = string.split("\n")
    # define max line length
    m_length = 0
    for i in strings:
        if len(i) > m_length:
            m_length = len(i)
    if title is None:
        print("+" * m_length + "++" + margin[0] * "+" + margin[1] * "+")
    else:
        print("+" + margin[0] * " " + (" " * int((m_length - len(title)) * 0.5)) + title +
              (" " * (m_length - len(title) - int((m_length - len(title)) * 0.5))) + margin[1] * " " + "+")
    for i in range(margin[2]):
        print("+" + margin[0] * " " + m_length * " " + margin[1] * " " + "+")
    # print the actual string
    for i in strings:
        if centering == "left":
            print("+" + margin[0] * " " + i + (" " * (m_length - len(i))) + margin[1] * " " + "+")
        elif centering == "center":
            print("+" + margin[0] * " " + (" " * int((m_length - len(i)) * 0.5)) + i +
                  (" " * (m_length - len(i) - int((m_length - len(i)) * 0.5))) + margin[1] * " " + "+")
        elif centering == "right":
            print("+" + margin[0] * " " + (" " * (m_length - len(i))) + i + margin[1] * " " + "+")
    for i in range(margin[3]):
        print("+" + margin[0] * " " + m_length * " " + margin[1] * " " + "+")
    print("+" * m_length + "++" + margin[0] * "+" + margin[1] * "+")


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def show_image(txt):
    with open(txt, "r") as f:
        for line in f.readlines():
            print(line, end="")
            sleep(0.01)
    return
