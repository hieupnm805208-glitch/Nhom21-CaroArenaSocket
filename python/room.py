class Room:
    SIZE = 15

    def __init__(self, room_id, player1):
        self.id = room_id
        self.player1 = player1
        self.player2 = None
        self.board = [[' ' for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.p1_turn = True

    def reset_board(self):
        self.board = [[' ' for _ in range(self.SIZE)] for _ in range(self.SIZE)]

    def add_player(self, player2):
        if self.player2 is None:
            self.player2 = player2
            return True
        return False

    def handle_move(self, player, r, c):
        symbol = 'X' if player == self.player1 else 'O'
        if self.is_valid_move(r, c) and self.is_player_turn(player):
            self.board[r][c] = symbol
            self.broadcast_move(r, c, symbol)
            if self.check_win(r, c, symbol):
                self.broadcast(f"WINNER:{symbol}")
                self.reset_board()
            else:
                self.p1_turn = not self.p1_turn

    def is_player_turn(self, p):
        return (p == self.player1 and self.p1_turn) or (p == self.player2 and not self.p1_turn)

    def is_valid_move(self, r, c):
        return 0 <= r < self.SIZE and 0 <= c < self.SIZE and self.board[r][c] == ' '

    def broadcast_move(self, r, c, symbol):
        msg = f"MOVE_UPDATE:{r},{c},{symbol}"
        self.broadcast(msg)

    def broadcast(self, msg):
        if self.player1:
            self.player1.send(msg)
        if self.player2:
            self.player2.send(msg)

    def check_win(self, r, c, s):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            if self.check_dir(r, c, dr, dc, s) + self.check_dir(r, c, -dr, -dc, s) >= 4:
                return True
        return False

    def check_dir(self, r, c, dr, dc, s):
        count = 0
        curr_r, curr_c = r + dr, c + dc
        while 0 <= curr_r < self.SIZE and 0 <= curr_c < self.SIZE and self.board[curr_r][curr_c] == s:
            count += 1
            curr_r += dr
            curr_c += dc
        return count
