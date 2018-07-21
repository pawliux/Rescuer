import os
from tkinter import *
from tkinter import filedialog

#functions
def openDir():
    d = filedialog.askdirectory()
    print(d)
    directory_entry.insert(0, d)

window = Tk()
window.geometry("640x480")

# openDir_frame = Frame(window)
# openDir_frame.grid(row=1, column=1, columnspan=4)
# openDir_frame.pack(pady=10)

directory_entry = Entry(window, width=50)
directory_entry.grid(row=1, column=1, columnspan=3)
#directory_entry.pack(side=LEFT, ipady=5, padx=10)
openDir_button = Button(window, text="Choose directory", command=openDir)
openDir_button.grid(row=1, column=5, sticky=W)
#openDir_button.pack(side=LEFT)



label = Label(window, text="testas")
# label.pack()

if __name__ == "__main__":
    window.mainloop()