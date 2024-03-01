import socket
import sys
from threading import Thread
import select
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import ftplib
import os
import ntpath
import time
from ftplib import FTP
from pathlib import Path


PORT  = 8010
IP_ADDRESS = '127.0.0.1'
SERVER = None

name = None
listbox =  None
textarea= None
labelchat = None
text_message = None
filePathLabel = None
sending_file = None
downloading_file = None
file_to_download = None

BUFFER_SIZE = 4096

def connectWithClient():
    global SERVER
    global listbox

    text=listbox.get(ANCHOR)
    list_item = text.split(":")
    msg="connect "+list_item[1]
    SERVER.send(msg.encode('ascii'))

def disconnectWithClient():
    global SERVER

    text=listbox.get(ANCHOR)
    list_item = text.split(":")
    msg="disconnect "+list_item[1]
    SERVER.send(msg.encode('ascii'))


def quitSession():
    global SERVER
    SERVER.close()

def getFileSize(file_name):
    with open(file_name, "rb") as file:
        chunk = file.read()
        return len(chunk)

def receiveMessage():
    global SERVER
    global name
    global textarea
    global BUFFER_SIZE

    while True:
        chunk = SERVER.recv(BUFFER_SIZE)
        try:
            if("tiul" in chunk.decode() and "1.0," not in chunk.decode()):
                letter_list = chunk.decode().split(",")
                listbox.insert(letter_list[0],letter_list[0]+":"+letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
                print(letter_list[0],letter_list[0]+":"+letter_list[1]+": "+letter_list[3]+" "+letter_list[5])
            else:
                textarea.insert(END,"\n"+chunk.decode('ascii'))
                textarea.see("end")
                print(chunk.decode('ascii'))
        except:
            pass



def browseFiles():
    global sending_file
    global textarea
    global filePathLabel
    try:
        filename = filedialog.askopenfilename()
        filePathLabel.configure(text = filename)
        HOSTNAME = "127.0.0.1"
        USERNAME = "lftpd"
        PASSWORD = "lftpd"
        ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
        ftp_server.encoding = "utf-8"
        ftp_server.cwd("shared_files")
        f_name = ntpath.basename(filename)
        with open(filename, "rb") as file:
            ftp_server.storbinary(f"STOR {f_name}", file)
        ftp_server.dir()
        ftp_server.quit()
        message = ("send " + f_name)
        if message[:4] == "send":
            print("Please Wait...\n")
            textarea.insert(END, "\n" + "\n Please Wait... \n")
            textarea.see("end")
            sending_file = message[5:]
            file_size = getFileSize("shared_files/" + sending_file)
            final_message = message + " " + str(file_size)
            SERVER.send(final_message.encode())
            textarea.insert(END, "File Succesfully Sent!")
    except FileNotFoundError:
        print("Cancel Button Pressed")
    

   


def sendMessage():
    global SERVER
    global textarea
    global text_message

    msgtosend = text_message.get()                                               

    SERVER.send(msgtosend.encode('ascii'))
    textarea.insert(END,"\n"+"You>"+msgtosend)
    textarea.see("end")
    text_message.delete(0, 'end')
    if msgtosend == "y" or msgtosend == "Y":
        textarea.insert(END, "\nPlease Wait... File is downloading...")
        textarea.see("end")
        HOSTNAME = "127.0.0.1"
        USERNAME = "lftpd"
        PASSWORD = "lftpd"
        home = str(Path.home())
        download_path = home + "\Downloads"
        ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
        ftp_server.encoding = "utf-8"
        ftp_server.cwd("shared_files")
        f_name = file_to_download
        local_file_name = os.path.join(download_path, f_name)
        file = open(local_file_name, "wb")
        ftp_server.retrbinary("Retr " + f_name, file.write())
        ftp_server.dir()
        file.close()
        ftp_server.quit()
        print("File Successfully Downloaded! " + download_path)
        textarea.insert(END, "\nFile Successfully Downloaded to path : " + download_path)
        textarea.see("end")

def showClientsList():
    global listbox
    listbox.delete(0,"end")
    SERVER.send("show list".encode('ascii'))


def connectToServer():
    global SERVER
    global name

    cname = name.get()
    SERVER.send(cname.encode())


def openChatWindow():

    print("\n\t\t\t\tIP MESSENGER")

   
    window=Tk()

    window.title('Messenger')
    window.geometry("500x350")

    global name
    global listbox
    global textarea
    global labelchat
    global text_message
    global filePathLabel

    namelabel = Label(window, text= "Enter Your Name", font = ("Calibri",10))
    namelabel.place(x=10, y=8)

    name = Entry(window,width =30,font = ("Calibri",10))
    name.place(x=120,y=8)
    name.focus()

    connectserver = Button(window,text="Connect to Chat Server",bd=1, font = ("Calibri",10), command = connectToServer)
    connectserver.place(x=350,y=6)

    separator = ttk.Separator(window, orient='horizontal')
    separator.place(x=0, y=35, relwidth=1, height=0.1)

    labelusers = Label(window, text= "Active Users", font = ("Calibri",10))
    labelusers.place(x=10, y=50)

    listbox = Listbox(window,height = 5,width = 67,activestyle = 'dotbox', font = ("Calibri",10))
    listbox.place(x=10, y=70)

    scrollbar1 = Scrollbar(listbox)
    scrollbar1.place(relheight = 1,relx = 1)
    scrollbar1.config(command = listbox.yview)

    connectButton=Button(window,text="Connect",bd=1, font = ("Calibri",10), command = connectWithClient)
    connectButton.place(x=282,y=160)

    disconnectButton=Button(window,text="Disconnect",bd=1, font = ("Calibri",10), command = disconnectWithClient)
    disconnectButton.place(x=350,y=160)

    refresh=Button(window,text="Refresh",bd=1, font = ("Calibri",10), command = showClientsList)
    refresh.place(x=435,y=160)

    labelchat = Label(window, text= "Chat Window", font = ("Calibri",10))
    labelchat.place(x=10, y=180)

    textarea = Text(window, width = 67,height = 6,font = ("Calibri",10))
    textarea.place(x=10,y=200)

    scrollbar2 = Scrollbar(textarea)
    scrollbar2.place(relheight = 1,relx = 1)
    scrollbar2.config(command = listbox.yview)

    
    attach=Button(window,text="Attach & Send",bd=1, font = ("Calibri",10), command = browseFiles)
    attach.place(x=10,y=305)

    text_message = Entry(window, width =43, font = ("Calibri",12))
    text_message.pack()
    text_message.place(x=98,y=306)

  
    send=Button(window,text="Send",bd=1, font = ("Calibri",10), command = sendMessage)
    send.place(x=450,y=305)

    filePathLabel = Label(window, text= "",fg= "blue", font = ("Calibri",8))
    filePathLabel.place(x=10, y=330)

    window.mainloop()


def setup():
    global SERVER
    global PORT
    global IP_ADDRESS

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.connect((IP_ADDRESS, PORT))

    receive_thread = Thread(target=receiveMessage)               #receiving multiple messages
    receive_thread.start()

    openChatWindow()

setup()
