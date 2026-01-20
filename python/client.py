import socket
import threading
import time
from gui import GameGUI

class Client:
    HOST = 'localhost'
    PORT = 12345

    def __init__(self):
        self.gui = None
        self.sock = None
        self.file = None

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.HOST, self.PORT))
            self.file = self.sock.makefile(mode='rw', encoding='utf-8')

            print("Connected to Caro Arena Server!")

            # Prompt for username instead of auto-generating
            import tkinter.simpledialog as sd
            temp_root = tk.Tk()
            temp_root.withdraw()
            username = sd.askstring("Login", "Enter your username:", parent=temp_root)
            temp_root.destroy()

            if not username:
                username = f"Player_{int(time.time() % 1000)}"

            self.send(f"LOGIN:{username}")
            
            # Auto join room 1
            self.send("JOIN_ROOM:1")

            self.gui = GameGUI(self)
            
            # Start listener thread
            threading.Thread(target=self.listen_to_server, daemon=True).start()
            
            self.gui.run()

        except Exception as e:
            print(f"Could not connect to server: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def listen_to_server(self):
        try:
            while True:
                line = self.file.readline()
                if not line:
                    break
                self.handle_server_message(line.strip())
        except Exception as e:
            print(f"Error reading from server: {e}")

    def handle_server_message(self, msg):
        print(f"Message from server: {msg}")
        if msg.startswith("JOIN_SUCCESS:"):
            parts = msg.split(":")
            room_id = parts[1]
            symbol = parts[2]
            self.gui.my_symbol = symbol
            # Use queue_update for thread safety
            self.gui.queue_update(self.gui.set_my_turn, symbol == 'X')
            self.gui.queue_update(self.gui.update_title, f"Room {room_id}")
        elif msg.startswith("MOVE_UPDATE:"):
            parts = msg[12:].split(",")
            r, c, s = int(parts[0]), int(parts[1]), parts[2]
            self.gui.queue_update(self.gui.update_board, r, c, s)
        elif msg.startswith("WINNER:"):
            symbol = msg[7:]
            self.gui.queue_update(self.gui.show_message, f"Player {symbol} Wins!")
        elif msg.startswith("CHAT_MSG:"):
            print(msg[9:])

    def send_move(self, r, c):
        self.send(f"MOVE:{r},{c}")

    def send(self, msg):
        try:
            self.file.write(msg + "\n")
            self.file.flush()
        except Exception as e:
            print(f"Send error: {e}")

if __name__ == "__main__":
    Client().start()
