import pygame
import socket
import json
import threading

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 10
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CROSS_WIDTH = SQUARE_SIZE // 3
OFFSET = SQUARE_SIZE // 3

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 150, 200)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe - Client")
screen.fill(BG_COLOR)

# Font
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 30)

class TicTacToeClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = input("Enter server IP: ")
        self.port = 30000
        
        self.player_symbol = None
        self.current_player = 0
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.winner = None
        self.opponent_rematch_request = False
        self.rematch_requested = False
        
        self.connect_to_server()
    
    def connect_to_server(self):
        try:
            self.client.connect((self.server_ip, self.port))
            print("Connected to server")
            
            # Start thread to receive messages from server
            receive_thread = threading.Thread(target=self.receive_data)
            receive_thread.daemon = True
            receive_thread.start()
        except Exception as e:
            print(f"Error connecting to server: {e}")
    
    def receive_data(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    break
                
                data = json.loads(data)
                
                if data['type'] == 'init':
                    self.player_symbol = data['symbol']
                    print(f"You are player {self.player_symbol}")
                elif data['type'] == 'game_state':
                    self.board = data['board']
                    self.current_player = data['current_player']
                    self.game_over = data['game_over']
                    self.winner = data['winner']
                    if not self.game_over:
                        self.rematch_requested = False
                        self.opponent_rematch_request = False
                elif data['type'] == 'error':
                    print(f"Error: {data['message']}")
                elif data['type'] == 'rematch_request':
                    self.opponent_rematch_request = True
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
    
    def send_move(self, row, col):
        if not self.game_over:
            data = {
                'type': 'move',
                'row': row,
                'col': col
            }
            self.client.send(json.dumps(data).encode())
    
    def send_rematch_request(self):
        data = {
            'type': 'rematch'
        }
        self.client.send(json.dumps(data).encode())
        self.rematch_requested = True
    
    def draw_board(self):
        # Draw horizontal lines
        pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
        
        # Draw vertical lines
        pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)
        
        # Draw X's and O's
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] == 'O':
                    pygame.draw.circle(screen, CIRCLE_COLOR, 
                                      (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                                      CIRCLE_RADIUS, LINE_WIDTH)
                elif self.board[row][col] == 'X':
                    pygame.draw.line(screen, CROSS_COLOR, 
                                    (col * SQUARE_SIZE + OFFSET, row * SQUARE_SIZE + OFFSET),
                                    (col * SQUARE_SIZE + SQUARE_SIZE - OFFSET, row * SQUARE_SIZE + SQUARE_SIZE - OFFSET),
                                    LINE_WIDTH)
                    pygame.draw.line(screen, CROSS_COLOR, 
                                    (col * SQUARE_SIZE + OFFSET, row * SQUARE_SIZE + SQUARE_SIZE - OFFSET),
                                    (col * SQUARE_SIZE + SQUARE_SIZE - OFFSET, row * SQUARE_SIZE + OFFSET),
                                    LINE_WIDTH)
        
        # Display game status
        if self.game_over:
            if self.winner:
                text = f"{self.winner} wins!" if self.winner != self.player_symbol else "You win!"
            else:
                text = "It's a tie!"
            
            text_surface = font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            pygame.draw.rect(screen, BG_COLOR, (WIDTH//4, HEIGHT//2 - 80, WIDTH//2, 60))
            screen.blit(text_surface, text_rect)
            
            # Draw rematch button
            rematch_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
            button_color = BUTTON_HOVER_COLOR if rematch_button.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
            pygame.draw.rect(screen, button_color, rematch_button, border_radius=5)
            
            rematch_text = "Rematch" if not self.rematch_requested else "Waiting..."
            rematch_surface = small_font.render(rematch_text, True, TEXT_COLOR)
            rematch_rect = rematch_surface.get_rect(center=rematch_button.center)
            screen.blit(rematch_surface, rematch_rect)
            
            # Show opponent rematch status
            if self.opponent_rematch_request and not self.rematch_requested:
                opponent_text = "Opponent wants rematch!"
                opponent_surface = small_font.render(opponent_text, True, TEXT_COLOR)
                opponent_rect = opponent_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
                screen.blit(opponent_surface, opponent_rect)
        else:
            if self.current_player == (0 if self.player_symbol == 'X' else 1):
                text = "Your turn"
            else:
                text = "Opponent's turn"
            
            text_surface = font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH//2, 20))
            pygame.draw.rect(screen, BG_COLOR, (WIDTH//4, 0, WIDTH//2, 40))
            screen.blit(text_surface, text_rect)
        
        pygame.display.update()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX, mouseY = pygame.mouse.get_pos()
                    
                    if self.game_over:
                        # Check if rematch button was clicked
                        rematch_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
                        if rematch_button.collidepoint(mouseX, mouseY) and not self.rematch_requested:
                            self.send_rematch_request()
                    else:
                        # Handle game moves
                        clicked_row = mouseY // SQUARE_SIZE
                        clicked_col = mouseX // SQUARE_SIZE
                        
                        if 0 <= clicked_row < 3 and 0 <= clicked_col < 3:
                            if self.current_player == (0 if self.player_symbol == 'X' else 1):
                                self.send_move(clicked_row, clicked_col)
            
            screen.fill(BG_COLOR)
            self.draw_board()
            pygame.display.update()
        
        pygame.quit()
        self.client.close()

if __name__ == "__main__":
    client = TicTacToeClient()
    client.run()
