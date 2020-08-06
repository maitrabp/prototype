from tkinter import filedialog
from tkinter import *
import tkinter.font as font
from parseTest import *
import subprocess, os, platform

ftypes = [
    ('PDF', '*.pdf')
]

def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global file_path
    filename = filedialog.askopenfile(filetypes=ftypes)
    file_path = filename.name
def program_instructions():
    print("=============================USER INSTRUCTIONS================================================")
    print("-  CLOSE THE MASTER CSV FILE PRIOR TO RUNNING THE PROGRAM, program cannot write to an open CSV file.")
    print("-  The program can ONLY handle readable PDF files (not image PDFs, textual only), therefore \nplease check before you feed in the files to the system.")
    print("-  Browse Button - This is used to navigate to your PDF file & get the path.")
    print("-  Submit Button - This is used to initiate the parser.")
    print("-  Open Button - This is used to open the CSV file after the data has been parsed and transferred into it.")
    print("-  NOTE: The CSV file is rewritten everytime the tool is ran, \nwhich means the old data is wiped out and new data is written based on the PDF uploaded.\nTherefore, it's best to save the CSV elsewhere before trying a second run.")
    print("==============================================================================================")
def run_prog():
    # This is your function maitra use the folder_path variable to get filename
    saveCSVfilepath = file_parse(file_path)
    finish_msg = StringVar()
    lbl2 = Label(master = root, textvariable=finish_msg, bg='#FED000', fg='black', font = font.Font(size=15), height= 3, highlightthickness = 0, bd = 0)
    finish_msg.set("MESSAGE: Your master CSV file is ready, \nClick on 'Open Master CSV' to open it! \n PATH: " + saveCSVfilepath)
    lbl2.pack()

def open_file():
    filepath = 'parseRESULT.csv'
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


root = Tk()
program_instructions()
myFont = font.Font(size=30)
root.geometry("500x950")
root.configure(bg='#1F1F1F')
root.title("TREASURY DATA PARSER")
file_path = StringVar()
file_path.set("WELCOME TO THE TREASURY DATA PARSER")
lbl1 = Label(master=root,textvariable=file_path, bg='#1F1F1F', fg='white', font = 30, height= 3)
lbl1.pack()

button2 = Button(text="Browse Audit File", command=browse_button, bg='#1F1F1F', fg='white', activebackground='#FF8000', highlightthickness = 0, bd = 0)
button2['font'] = myFont
button2.config(height=5, width = 20)
button2.pack()


button3 = Button(text="Submit", command=run_prog, bg='#1F1F1F', fg='white', activebackground='#FF8000', highlightthickness = 0, bd = 0) # put your function name in the command option maitra
button3['font'] = myFont
button3.config(height=5, width = 20)
button3.pack()

button4 = Button(text="Open Master CSV", command=open_file, bg='#1F1F1F', fg='white', activebackground='#FF8000', highlightthickness = 0, bd = 0) # put your function name in the command option maitra
button4['font'] = myFont
button4.config(height=5, width = 20)
button4.pack()


mainloop()