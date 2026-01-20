import socket
import threading
from room import Room

class Server:
    PORT = 12345
    HOST = '0.0.0.0'

    def __init__(self):
        self.clients = []
        self.rooms = []
        self.lock = threading.Lock()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.HOST, self.PORT))
        server_socket.listen(5)
        print(f"Caro Arena Server is running on port {self.PORT}")

        try:
            while True:
                client_sock, addr = server_socket.accept()
                print(f"New client connected: {addr}")
                handler = ClientHandler(client_sock, self)
                with self.lock:
                    self.clients.append(handler)
                threading.Thread(target=handler.run, daemon=True).start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            server_socket.close()

    def remove_client(self, handler):
        with self.lock:
            if handler in self.clients:
                self.clients.remove(handler)

    def join_room(self, client, room_id):
        with self.lock:
            for room in self.rooms:
                if room.id == room_id:
                    if room.add_player(client):
                        client.current_room = room
                        client.send(f"JOIN_SUCCESS:{room_id}:O")
                        if room.player1:
                            room.player1.send(f"OPPONENT_JOINED:{client.username}")
                        return
                    else:
                        client.send("ERROR:Room is full")
                        return
            
            # Create new room if not found
            new_room = Room(room_id, client)
            self.rooms.append(new_room)
            client.current_room = new_room
            client.send(f"JOIN_SUCCESS:{room_id}:X")

class ClientHandler:
    def __init__(self, sock, server):
        self.sock = sock
        self.server = server
        self.username = None
        self.current_room = None
        self.file = sock.makefile(mode='rw', encoding='utf-8')

    def run(self):
        try:
            self.send("WELCOME:Welcome to Caro Arena!")
            while True:
                line = self.file.readline()
                if not line:
                    break
                message = line.strip()
                if message:
                    self.process_message(message)
        except Exception as e:
            print(f"Connection lost with {self.username or 'unknown'}: {e}")
        finally:
            self.cleanup()

    def process_message(self, message):
        if message.startswith("LOGIN:"):
            self.username = message[6:]
            self.send(f"LOGIN_SUCCESS:{self.username}")
        elif message.startswith("JOIN_ROOM:"):
            try:
                room_id = int(message[10:])
                self.server.join_room(self, room_id)
            except ValueError:
                self.send("ERROR:Invalid room ID")
        elif message.startswith("MOVE:"):
            if self.current_room:
                try:
                    parts = message[5:].split(",")
                    r, c = map(int, parts)
                    self.current_room.handle_move(self, r, c)
                except (ValueError, IndexError):
                    pass
        elif message.startswith("CHAT:"):
            if self.current_room:
                chat_msg = f"CHAT_MSG:{self.username}: {message[5:]}"
                self.current_room.broadcast(chat_msg)

    def send(self, msg):
        try:
            self.file.write(msg + "\n")
            self.file.flush()
        except:
            pass

    def cleanup(self):
        self.server.remove_client(self)
        try:
            self.sock.close()
        except:
            pass

if __name__ == "__main__":
    Server().start()
