import pygame
import sys
import Position
import Solver

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Kích thước
SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)
WIDTH = 7 * SQUARESIZE
HEIGHT = 7 * SQUARESIZE  

class Connect4UI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Connect 4 - Human vs AI")
        self.font = pygame.font.SysFont("Arial", 36)
        self.position = Position.Position()
        self.solver = Solver.Solver()
        self.game_over = False
        self.current_player = 1  # 1: Human, 2: AI
        self.clock = pygame.time.Clock()
        
    def draw_board(self):
        # Vẽ nền
        self.screen.fill(BLACK)
        
        # Vẽ các ô trống
        for col in range(Position.Position.WIDTH):
            for row in range(Position.Position.HEIGHT):
                pygame.draw.rect(self.screen, BLUE, 
                               (col * SQUARESIZE, (row + 1) * SQUARESIZE, 
                                SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(self.screen, BLACK, 
                                 (col * SQUARESIZE + SQUARESIZE // 2, 
                                  (row + 1) * SQUARESIZE + SQUARESIZE // 2), 
                                 RADIUS)
        
        # Vẽ các quân cờ
        for col in range(Position.Position.WIDTH):
            for row in range(Position.Position.HEIGHT):
                pos = col * (Position.Position.HEIGHT + 1) + row
                if (self.position.mask >> pos) & 1:
                    if (self.position.current_position >> pos) & 1:
                        color = RED  # Người chơi
                    else:
                        color = YELLOW  # AI
                    
                    pygame.draw.circle(self.screen, color,
                                     (col * SQUARESIZE + SQUARESIZE // 2,
                                      HEIGHT - (row * SQUARESIZE + SQUARESIZE // 2)),
                                     RADIUS)
        
        # Vẽ quân cờ di chuyển khi rê chuột
        if not self.game_over and self.current_player == 1:
            posx = pygame.mouse.get_pos()[0]
            pygame.draw.circle(self.screen, RED, 
                             (posx, SQUARESIZE // 2), RADIUS)
        
        pygame.display.update()
    
    def handle_human_move(self, col):
        if  self.position.is_winning_move(col):
            self.position.playCol(col)
            self.game_over = True
            self.draw_board()
            self.show_message("Bạn thắng!")
        elif self.position.nb_moves() == Position.Position.WIDTH * Position.Position.HEIGHT:
            self.game_over = True
            self.draw_board()
            self.show_message("Hòa!")
        self.position.playCol(col)
        self.current_player = 2
        
    def ai_move(self):
        print("AI đang suy nghĩ...")
        best_col = None
        best_score = -float('inf')
        
        for col in range(Position.Position.WIDTH):
            if self.position.can_play(col) and self.position.is_winning_move(col):
                best_col = col
                self.position.playCol(best_col)
                self.game_over = True
                self.draw_board()
                self.show_message("AI thắng!")
                break
        
        for x in range(Position.Position.WIDTH):
            col = self.solver.column_order[x]
            if self.position.can_play(col):
                P2 = Position.Position(self.position)
                P2.playCol(col)
                
                opponent_can_win = False
                for y in range(Position.Position.WIDTH):
                    if P2.can_play(y) and P2.is_winning_move(y):
                        opponent_can_win = True
                        break
                
                if not opponent_can_win:
                    score = -self.solver.solve(P2)
                    if score > best_score or best_col is None:
                        best_col = col
                        best_score = score
        
        if best_col is None:
            for col in range(Position.Position.WIDTH):
                if self.position.can_play(col):
                    best_col = col
                    break
        
        self.position.playCol(best_col)
        self.position.print_board()
        print(f"AI chọn cột {best_col + 1}")

        if self.position.nb_moves() == Position.Position.WIDTH * Position.Position.HEIGHT:
            self.game_over = True
            self.draw_board()
            self.show_message("Hòa!")

        self.current_player = 1  
    
    def show_message(self, text):
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        label = self.font.render(text, True, WHITE)
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 10))
        pygame.display.update()
        pygame.time.wait(3000)
    
    def reset_game(self):
        self.position = Position.Position()
        self.game_over = False
        self.current_player = 1
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.current_player == 1:
                    posx = event.pos[0]
                    col = posx // SQUARESIZE
                    self.handle_human_move(col)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Nhấn R để chơi lại
                        self.reset_game()
                    elif event.key == pygame.K_q:  # Nhấn Q để thoát
                        pygame.quit()
                        sys.exit()
            
            if not self.game_over and self.current_player == 2:
                self.ai_move()
            
            if not self.game_over:
                self.draw_board()
                self.clock.tick(60)