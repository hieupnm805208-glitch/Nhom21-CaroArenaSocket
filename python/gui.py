import tkinter as tk
from tkinter import messagebox

class GameGUI:
    SIZE = 15

    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Caro Arena")
        self.my_turn = False
        self.my_symbol = ' '
        self.buttons = [[None for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self._setup_ui()

    def _setup_ui(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                btn = tk.Button(self.root, text='', font=('Arial', 14, 'bold'), width=2, height=1,
                               command=lambda r=i, c=j: self.on_click(r, c))
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

    def on_click(self, r, c):
        if self.my_turn and self.buttons[r][c]['text'] == '':
            self.buttons[r][c].config(text=self.my_symbol)
            self.client.send_move(r, c)
            self.set_my_turn(False)

    def set_my_turn(self, turn):
        self.my_turn = turn
        self.update_title()

    def update_title(self, extra=""):
        status = "Your Turn" if self.my_turn else "Opponent's Turn"
        title = f"Caro Arena - {status} ({self.my_symbol})"
        if extra:
            title += f" - {extra}"
        self.root.title(title)

    def queue_update(self, func, *args):
        """Schedule a function to run on the main UI thread."""
        self.root.after(0, func, *args)

    def update_board(self, r, c, symbol):
        self.buttons[r][c].config(text=symbol)
        if symbol != self.my_symbol:
            self.set_my_turn(True)

    def show_message(self, msg):
        messagebox.showinfo("Caro Arena", msg)

    def run(self):
        self.root.mainloop()

    def set_title(self, title):
        self.root.title(title)
