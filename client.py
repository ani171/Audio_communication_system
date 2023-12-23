import socket
import threading
import pickle
from pynput import keyboard
import pyautogui
import pyaudio
import time

global connected

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
HEADER = 1024
PORT = 19699
SERVER = "192.168.136.230" 
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"
connected = True
PAYLOAD_BITS = 8
talking = False

audio = pyaudio.PyAudio()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

input_stream = audio.open(format=FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        input = True)

output_stream = audio.open(format=FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        output = True)

def stopRecord(key):
    global talking
    try:
        talking = False
        print("STOPPING")
    except AttributeError:
        pass


def record(key):
    global talking
    global connected
    try:
        if(key == keyboard.Key.shift_r):
            talking=True
            with keyboard.Listener(on_release=stopRecord) as listener:
                while talking:
                    data = input_stream.read(HEADER, exception_on_overflow = False)
                    data = pickle.dumps(data)

                    send_length = str(len(data)).encode('utf-8')
                    print(f"\x1b[31mSending {send_length} bytes\x1b[0m")
                    send_length = b' '*(PAYLOAD_BITS-len(send_length)) + send_length
                    message = send_length+data
                    print(f"\x1b[31mSending message: {message}\x1b[0m")
                    client.sendall(message)

        elif(key.char == 'x'):
            print("DISCONNECTING")
            data = pickle.dumps(DISCONNECT_MESSAGE)
            send_length = str(len(data)).encode('utf-8')
            send_length = b' '*(PAYLOAD_BITS-len(send_length)) + send_length
            message = send_length+data
            client.send(message)
            connected=False
            talking=False

            input_stream.stop_stream()
            input_stream.close()
            output_stream.stop_stream()
            output_stream.close()
            output_wavefile.close()
            audio.terminate()
    except:
        print("Press Left Shift To Talk")

def setup():
    global connected
    with keyboard.Listener(on_press=record) as listener:
        while connected:
            pass
        client.close()

def listenToServer():
    global connected

    data = b''
    while connected:
        try:
            data += client.recv(HEADER)
            msg_length = int(data[:PAYLOAD_BITS])
            data = data[PAYLOAD_BITS:]
            while len(data)<msg_length:
                data += client.recv(HEADER)

            sample = pickle.loads(data)
            data = data[msg_length:]
            print(f"\x1b[32mReceived Message: {sample}\x1b[0m")
            output_stream.write(sample)
        except ValueError:
            print(f"DATA RECIEVED IS {data}")

thread = threading.Thread(target=setup)
thread2 = threading.Thread(target=listenToServer)
thread.start()
thread2.start()
