import socket
import pygame
import pickle
import hashlib


class Client:
    def __init__(self, server_ip, port_no):
        self.server_ip = server_ip
        self.port_no = port_no
        self.data_buffer = b''
        self.curr_mouse_x = 0
        self.curr_mouse_y = 0
        self.capslock_state = False
        self.key_event = {
            "key_code": pygame.K_0,
            "capslock_state": False,
            "modifiers": []
        }
        self.connection = False  # Initialize the connection attribute

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def send_password(self, s, password):
        hashed_password = self.hash_password(password)
        print(hashed_password)
        s.send(hashed_password.encode() + b"EndOfPassword")

    def listen_for_message(self, s):
        while True:
            new_data = s.recv(10000)
            self.data_buffer += new_data
            if b"PasswordFlag" in new_data:
                self.handle_authentication(s)
                break

    def handle_authentication(self, s):
        while True:
            authentication_message_bytes = self.data_buffer[:self.data_buffer.index(b"PasswordFlag")]
            self.data_buffer = self.data_buffer[self.data_buffer.index(b"PasswordFlag")+len(b"PasswordFlag"):]
            authentication_message = authentication_message_bytes.decode()
            if authentication_message == 'Wrong password':
                print("Wrong password entered, terminating session")
                break
            else:
                self.connection = True
                break

    def listen_for_image(self, s):
        while True:
            new_data = s.recv(10000)
            self.data_buffer += new_data
            if b"EndofImageFileFlag" in new_data:
                print("FOUND")
                break
        data = self.data_buffer[:self.data_buffer.index(b"EndofImageFileFlag")]
        self.data_buffer = self.data_buffer[self.data_buffer.index(b"EndofImageFileFlag")+len(b"EndofImageFileFlag"):]
        return data

    def handle_image(self, data):
        try:
            image_surface = pygame.image.fromstring(data, (960, 540), "RGB")
            print("Successful")
        except Exception as e:
            print("Error")
        screen = pygame.display.set_mode((640, 360))
        scaled_image = pygame.transform.smoothscale(image_surface, (640, 360))
        screen.fill((0, 0, 0))
        screen.blit(scaled_image, (0, 0))
        pygame.display.flip()

    def send_mouse_position(self, s):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x == 0 or mouse_x == 640 or mouse_y == 0 or mouse_y == 360:
            return
        if mouse_x == self.curr_mouse_x and mouse_y == self.curr_mouse_y:
            return
        print("Sending mouse position")
        mouse_pos = {"x": mouse_x, "y": mouse_y}
        pos_bytes = pickle.dumps(mouse_pos)
        s.send(pos_bytes + b"EndOfMousePos")
        self.curr_mouse_x = mouse_x
        self.curr_mouse_y = mouse_y

    def send_event(self, s):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                button = event.button
                print(button)
                mouse_click = {"x": mouse_x, "y": mouse_y, "button": button}
                event_bytes = pickle.dumps(mouse_click)
                s.send(event_bytes + b"EndOfMouseClick")
            if event.type == pygame.KEYDOWN:
                print("Sending key")
                key_code = event.key
                if key_code == pygame.K_LSHIFT or key_code == pygame.K_RSHIFT:
                    self.key_event["modifiers"].append('shift')
                elif key_code == pygame.K_LCTRL or key_code == pygame.K_RCTRL:
                    self.key_event["modifiers"].append('ctrl')
                elif key_code == pygame.K_LALT or key_code == pygame.K_RALT:
                    self.key_event["modifiers"].append('alt')
                elif key_code == pygame.K_CAPSLOCK:
                    self.capslock_state = not self.capslock_state
                else:
                    self.key_event = {"key_code": key_code, "capslock_state": self.capslock_state, "modifiers": self.key_event["modifiers"]}
                    key_bytes = pickle.dumps(self.key_event)
                    s.send(key_bytes + b"EndOfKeyStroke")
                    self.key_event["modifiers"].clear()

    def start(self, password):
        pygame.init()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.server_ip, self.port_no))
            print("Connected to server")
        except socket.error as e:
            print(f"Connection failed: {e}")
            self.connection = False
            return
        
        self.send_password(s, password)
        self.listen_for_message(s)
        
        if not self.connection:
            return
        
        print("Correct password, you may proceed")
        while True:
            print("Ready to receive")
            data = self.listen_for_image(s)
            self.handle_image(data)
            self.send_mouse_position(s)
            self.send_event(s)
        s.close()

if __name__ == "__main__":
    client = Client("192.168.1.11", 1234)
    password = input("Please input password: ")
    client.start(password)