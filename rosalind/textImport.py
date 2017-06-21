from tkinter import Tk, filedialog
from os import system
from platform import system as platform

root = Tk()
root.withdraw()

def getTextFile():
    if platform() == 'Darwin':
        system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    else:
        root.lift()
    filename = filedialog.askopenfilename()
    if filename[-3:] != 'txt':
        print("Please select a txt file.")
        raise SystemExit()
    text = open(filename, 'r')
    return(text.read())
