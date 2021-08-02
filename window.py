try:
    import Tkinter as tk
except ModuleNotFoundError:
    import tkinter as tk

class Dialog():

    def __init__(self, title, message, command1=self.ok, command2=self.ok, command3=self.ok, buttontext1="button1", buttontext2="button2", buttontext3="button3"):
        self.base = tk.Toplevel()
        self.base.title(title)
        self.label = tk.Label(self.base, text=message)
        self.label.pack()
        self.label.grid(row=0, column=0, columnspan=3, sticky=N)
        self.button1 = tk.Button(self.base, text=buttontext1, command=command1)
        self.button1.pack()
        self.button1.grid(row=1, column=0, sticky=N)
        self.button2 = tk.Button(self.base, text=buttontext2, command=command2)
        self.button2.pack()
        self.button2.grid(row=1, column=1, sticky=N)
        self.button3 = tk.Button(self.base, text=buttontext3, command=command3)
        self.button3.pack()
        self.button3.grid(row=1, column=2, sticky=N)
    def ok(self, event=None):
        self.destroy()
    def baseconfig(self, option, value):
        self.base[option] = value
    def labelconfig(self, option, value):
        self.label[option] = value
    def buttonconfig(self, number, option, value):
        pass
if __name__ == "__main__":
    window = Dialog()