from tkinter import Tk, Label, Button, Radiobutton, IntVar
#    ^ Use capital T here if using Python 2.7

def multipleChoice(prompt, options):
    root = Tk()
    if prompt:
        Label(root, text=prompt).pack()
    v = IntVar()
    for i, option in enumerate(options):
        Radiobutton(root, text=option, variable=v, value=i).pack(anchor="w")
    Button(text="Ok", command=root.destroy).pack()
    root.mainloop()
    if v.get() == 0: return None
    return options[v.get()]


if __name__ == "__main__":

    result = multipleChoice(
        "What is your favorite color?",
        [
            "Blue!",
            "No -- Yellow!",
            "Aaaaargh!"
        ]
    )

    print("User's response was: {}".format(repr(result)))
