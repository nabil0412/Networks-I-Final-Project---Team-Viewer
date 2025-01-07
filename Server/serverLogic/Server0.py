import socket
import pyautogui
import time
import pickle
from threading import Thread
from pynput.mouse import Controller
import pygame
import hashlib


class Server:
    def __init__(self, server_ip, port_no, password):
        ipConfig = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ipConfig.connect(("8.8.8.8", 80))
        ipConfig.getsockname()[0]
        self.server_ip = ipConfig.getsockname()[0]
        ipConfig.close()
        self.port_no = port_no
        self.password = password
        self.data_buffer = b''
        self.mouse_controller = Controller()
        self.connection = False
        self.key_mapping = {
            pygame.K_a: 'a',
            pygame.K_b: 'b',
            pygame.K_c: 'c',    
            pygame.K_d: 'd',
            pygame.K_e: 'e',
            pygame.K_f: 'f',
            pygame.K_g: 'g',
            pygame.K_h: 'h',
            pygame.K_i: 'i',
            pygame.K_j: 'j',
            pygame.K_k: 'k',
            pygame.K_l: 'l',
            pygame.K_m: 'm',
            pygame.K_n: 'n',
            pygame.K_o: 'o',
            pygame.K_p: 'p',
            pygame.K_q: 'q',
            pygame.K_r: 'r',
            pygame.K_s: 's',
            pygame.K_t: 't',
            pygame.K_u: 'u',
            pygame.K_v: 'v',
            pygame.K_w: 'w',
            pygame.K_x: 'x',
            pygame.K_y: 'y',
            pygame.K_z: 'z',
            pygame.K_1: '1',
            pygame.K_2: '2',
            pygame.K_3: '3',
            pygame.K_4: '4',
            pygame.K_5: '5',
            pygame.K_6: '6',
            pygame.K_7: '7',
            pygame.K_8: '8',
            pygame.K_9: '9',
            pygame.K_0: '0',
            pygame.K_SPACE: ' ',  # Space key
            pygame.K_RETURN: '\n',  # Enter key
            pygame.K_BACKSPACE: '\b',  # Backspace
            pygame.K_TAB: '\t',  # Tab
            pygame.K_BACKQUOTE: '`',
            pygame.K_MINUS: '-',     
            pygame.K_EQUALS: '=',    
            pygame.K_LEFTBRACKET: '[', 
            pygame.K_RIGHTBRACKET: ']',
            pygame.K_BACKSLASH: '\\', 
            pygame.K_SEMICOLON: ';',  
            pygame.K_QUOTE: '\'',     
            pygame.K_COMMA: ',',      
            pygame.K_PERIOD: '.',     
            pygame.K_SLASH: '/',
            pygame.K_F1: 'F1',
            pygame.K_F2: 'F2',
            pygame.K_F3: 'F3',
            pygame.K_F4: 'F4',
            pygame.K_F5: 'F5',
            pygame.K_F6: 'F6',
            pygame.K_F7: 'F7',
            pygame.K_F8: 'F8',
            pygame.K_F9: 'F9',
            pygame.K_F10: 'F10',
            pygame.K_F11: 'F11',
            pygame.K_F12: 'F12'
        }

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def listen_for_data(self, s):
        while True:
            print("Receiving data")
            new_data = s.recv(10000)
            self.data_buffer += new_data
            if b"EndOfMousePos" in self.data_buffer:
                self.handle_mouse_position()
            if b"EndOfMouseClick" in self.data_buffer:
                self.handle_mouse_click()
            if b"EndOfKeyStroke" in self.data_buffer:
                self.handle_key_strokes()

    def listen_for_password(self, s):
        while True:
            print("Receiving password")
            new_data = s.recv(10000)
            self.data_buffer += new_data
            if b"EndOfPassword" in self.data_buffer:
                self.handle_password(s)
                break

    def handle_password(self, s):
        password_bytes = self.data_buffer[:self.data_buffer.index(b"EndOfPassword")]
        self.data_buffer = self.data_buffer[self.data_buffer.index(b"EndOfPassword")+len(b"EndOfPassword"):]
        received_password = password_bytes.decode()
        hashed_password = self.hash_password(self.password)
        if hashed_password != received_password:
            s.send("Wrong password".encode() + b"PasswordFlag")
            s.close()
            print("Incorrect password, terminating session")
            quit()
        else:
            s.send("Correct password".encode() + b"PasswordFlag")

    def handle_mouse_position(self):
        print("Received mouse data")
        mouse_pos_bytes = self.data_buffer[:self.data_buffer.index(b"EndOfMousePos")]
        self.data_buffer = self.data_buffer[self.data_buffer.index(b"EndOfMousePos")+len(b"EndOfMousePos"):]
        mouse_pos = pickle.loads(mouse_pos_bytes)
        try:
            mouse_x = mouse_pos["x"] * 3
            mouse_y = mouse_pos["y"] * 3
            pyautogui.moveTo(mouse_x, mouse_y)
        except:
            print("Couldn't move mouse")
            self.handle_key_strokes()

    def handle_mouse_click(self):
        print("Received mouse data")
        mouse_click_bytes = self.data_buffer[:self.data_buffer.index(b"EndOfMouseClick")]
        self.data_buffer = self.data_buffer[self.data_buffer.index(b"EndOfMouseClick")+len(b"EndOfMouseClick"):]
        mouse_click = pickle.loads(mouse_click_bytes)
        button_no = mouse_click["button"]
        button_name = ""
        if button_no == 1:
            button_name = "left"
        if button_no == 2:
            button_name = "middle"
        if button_no == 3:
            button_name = "right"
        if 1 <= button_no <= 3:
            pyautogui.click(button=button_name)
        if button_no == 4:
            self.mouse_controller.scroll(0, 3)
        if button_no == 5:
            self.mouse_controller.scroll(0, -3)

    def handle_key_strokes(self):
        print("Sending Key")
        key_stroke_bytes = self.data_buffer[:self.data_buffer.index(b"EndOfKeyStroke")]
        self.data_buffer = self.data_buffer[self.data_buffer.index(b"EndOfKeyStroke")+len(b"EndOfKeyStroke"):]
        key_stroke = pickle.loads(key_stroke_bytes)
        key_code = key_stroke["key_code"]
        print(key_code)
        capslock_state = key_stroke["capslock_state"]
        modifiers = key_stroke["modifiers"]
        key = self.key_mapping[key_code]
        key = key.lower()
        if capslock_state:
            key = key.upper()
        if len(modifiers) == 0:
            pyautogui.press(key)
        else:
            pyautogui.hotkey(*modifiers, key)

    def send_thread(self, s):
        while True:
            screenshot = pyautogui.screenshot()
            screenshot = screenshot.resize((960, 540))
            img_bytes = screenshot.tobytes()
            s.sendall(img_bytes + b"EndofImageFileFlag")
            print("Sent image")
            time.sleep(1 / 100)

    def receive_thread(self, s):
        print("Receive Thread")
        while True:
            self.listen_for_data(s)
            print("Done listening")

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.server_ip, self.port_no))
        server_socket.listen(5)
        print("Server is listening...")
        s, address = server_socket.accept()
        print(f"Connection from {address} has been established.")
        connection = True
        self.listen_for_password(s)
        t1 = Thread(target=self.send_thread, args=(s,))
        t2 = Thread(target=self.receive_thread, args=(s,))
        t1.start()
        t2.start()

if __name__ == "__main__":
    server = Server(None, 1234, "ABCD")
    print("Server Ip Address: ", server.server_ip)
    server.start()
