from tkinter import filedialog
from tkinter import *
from parseTest import *
def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global file_path
    filename = filedialog.askopenfile()
    file_path = filename.name

def run_prog():
    # This is your function maitra use the folder_path variable to get filename
    saveCSVfilepath = file_parse(file_path)
    finish_msg = StringVar()
    lbl2 = Label(master = root, textvariable=finish_msg)
    finish_msg.set("MESSAGE: Your csv file is ready, go to " + saveCSVfilepath + " to take a look at!")
    lbl2.grid(row=3, column=3)

root = Tk()
root.title("TREASURY DATA PARSER")
file_path = StringVar()
file_path.set("WELCOME TO TREASURY DATA PARSER")
lbl1 = Label(master=root,textvariable=file_path)
lbl1.grid(row=0, column=3)
button2 = Button(text="Browse", command=browse_button)
button2.grid(row=1, column=3)
button3 = Button(text="Submit", command=run_prog) # put your function name in the command option maitra
button3.grid(row=2, column=3)

mainloop()
