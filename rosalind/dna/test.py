from os import system
from platform import system as platform

from tkinter import Tk
from tkinter import filedialog

root = Tk()
root.withdraw()

if platform() == 'Darwin':  # How Mac OS X is identified by Python
    system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
else:
    root.lift()

filename = filedialog.askopenfilename()

print(filename)
