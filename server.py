import socket
import threading
import json

class TicTacToeServer:
    def __init__(self):
        self.host = '192.168.53.15'
        self.port = 30000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(2)
        print("Server started, waiting for connections...")
        
        self.players = []
        self.rematch_requests = [False, False]
        self.current_player = 0
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.winner = None
        
    def handle_client(self, conn, player):
        try:
            # Send player their assigned symbol (X or O)
            symbol = 'X' if player == 0 else 'O'
            conn.send(json.dumps({'type': 'init', 'symbol': symbol}).encode())
            
            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    
                    data = json.loads(data)
                    
                    if data['type'] == 'move':
                        if player == self.current_player:
                            row, col = data['row'], data['col']
                            if self.is_valid_move(row, col):
                                self.board[row][col] = symbol
                                self.current_player = 1 - self.current_player
                                
                                # Check for winner or tie
                                self.check_game_over()
                                
                                # Broadcast updated game state
                                self.broadcast_game_state()
                        else:
                            conn.send(json.dumps({'type': 'error', 'message': 'Not your turn'}).encode())
                    elif data['type'] == 'rematch':
                        self.handle_rematch(player)
                except Exception as e:
                    print(f"Error handling client {player}: {e}")
                    break
        finally:
            conn.close()
            self.players[player] = None
            print(f"Player {player} disconnected")
    
    def handle_rematch(self, player):
        self.rematch_requests[player] = True
        if all(self.rematch_requests) and len(self.players) == 2:
            # Reset game state
            self.board = [[' ' for _ in range(3)] for _ in range(3)]
            self.game_over = False
            self.winner = None
            self.current_player = 0
            self.rematch_requests = [False, False]
            self.broadcast_game_state()
        else:
            # Notify players about rematch request
            for i, player_conn in enumerate(self.players):
                if player_conn:
                    try:
                        player_conn.send(json.dumps({
                            'type': 'rematch_request',
                            'player': player
                        }).encode())
                    except:
                        self.players[i] = None
    
    def is_valid_move(self, row, col):
        return 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == ' '
    
    def check_game_over(self):
        # Check rows
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != ' ':
                self.winner = self.board[row][0]
                self.game_over = True
                return
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != ' ':
                self.winner = self.board[0][col]
                self.game_over = True
                return
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            self.winner = self.board[0][0]
            self.game_over = True
            return
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            self.winner = self.board[0][2]
            self.game_over = True
            return
        
        # Check for tie
        if all(self.board[row][col] != ' ' for row in range(3) for col in range(3)):
            self.game_over = True
    
    def broadcast_game_state(self):
        game_state = {
            'type': 'game_state',
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner
        }
        
        for i, player_conn in enumerate(self.players):
            if player_conn:
                try:
                    player_conn.send(json.dumps(game_state).encode())
                except:
                    self.players[i] = None
    
    def start(self):
        while len(self.players) < 2:
            conn, addr = self.server.accept()
            print(f"New connection from {addr}")
            
            player = len(self.players)
            self.players.append(conn)
            
            threading.Thread(target=self.handle_client, args=(conn, player)).start()
            
            if len(self.players) == 2:
                print("Game starting...")
                self.broadcast_game_state()

if __name__ == "__main__":
    server = TicTacToeServer()
    server.start()
