import pygame
import sys
import Position
import Solver

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
COLORTEXT = BLACK

# Kích thước
SQUARESIZE = 120
RADIUS = int(SQUARESIZE/2 - 5)
WIDTH = 7 * SQUARESIZE
HEIGHT = 7 * SQUARESIZE  

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_hover):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.text_hover = text_hover
        self.font = pygame.font.Font('D:\AI_Connect_Four\Coiny.ttf', 36)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        color_text = self.text_hover if self.is_hovered else WHITE
        text_surface = self.font.render(self.text, True, color_text)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Connect4UI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Connect 4")
        self.font = pygame.font.Font('D:\AI_Connect_Four\Coiny.ttf', 36)
        self.clock = pygame.time.Clock()
        self.game_mode = None  
        self.setup_menu()

    def setup_menu(self):
        self.title_font = pygame.font.Font('D:\AI_Connect_Four\Coiny.ttf', 48)
        self.title_font.set_bold(True)
        
        button_width = 200
        button_height = 80
        
        self.pvp_button = Button(60, 680, button_width, button_height, 
                               "VS Player", BLUE, (0, 0, 200),COLORTEXT)
        self.pvc_button = Button(320, 680, button_width, button_height, 
                               "VS AI", BLUE,  (0, 0, 200),COLORTEXT)
        self.quit_button = Button(580, 680, button_width, button_height, 
                                "Quit", BLUE,  (0, 0, 200),COLORTEXT)
        
    def setup_game(self):
        self.position = Position.Position()
        self.solver = Solver.Solver()
        self.game_over = False
        self.current_player = 1  # 1: Human/X, 2: Human/O hoặc AI

    def draw_menu(self):
        background = pygame.transform.scale(pygame.image.load("Connect4.png"), (WIDTH, HEIGHT))
        self.screen.blit(background, (0, 0))
        
        # Vẽ tiêu đề
        title = self.title_font.render("CONNECT 4", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Vẽ các nút
        self.pvp_button.draw(self.screen)
        self.pvc_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        
        pygame.display.update()

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
                    is_current = (self.position.current_position >> pos) & 1
                    if (is_current and self.position.popcount(self.position.mask) % 2 == 0) or (not is_current and self.position.popcount(self.position.mask) % 2 == 1):
                        color = RED
                    else:
                        color = YELLOW
                    
                    pygame.draw.circle(self.screen, color,
                                     (col * SQUARESIZE + SQUARESIZE // 2,
                                      HEIGHT - (row * SQUARESIZE + SQUARESIZE // 2)),
                                     RADIUS)
        
        # Vẽ quân cờ di chuyển khi rê chuột
        if not self.game_over and (self.game_mode == 'pvp' or self.current_player == 1):
            posx = pygame.mouse.get_pos()[0]
            color = RED if self.current_player == 1 else YELLOW
            pygame.draw.circle(self.screen, color, 
                                (posx, SQUARESIZE // 2), RADIUS)
        
        pygame.display.update()
    
    def handle_human_move(self, col):

        if  self.position.is_winning_move(col):
            self.position.playCol(col)
            self.game_over = True
            self.draw_board()
            if self.game_mode == "pvp":
                self.show_message("Player " + str(self.current_player) + " win!")
            else:
                self.show_message("Player win!")
        elif self.position.nb_moves() == Position.Position.WIDTH * Position.Position.HEIGHT:
            self.game_over = True
            self.draw_board()
            self.show_message("Draw!")
        self.position.playCol(col)
        if self.current_player == 1:
            self.current_player = 2
        else: 
            self.current_player= 1
        
    def ai_move(self):
        self.show_message("AI thinking...")
        best_col = None
        best_score = -float('inf')
        
        for col in range(Position.Position.WIDTH):
            if self.position.can_play(col) and self.position.is_winning_move(col):
                best_col = col
                self.position.playCol(best_col)
                self.game_over = True
                self.draw_board()
                self.show_message("AI win!")
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

        if self.position.nb_moves() == Position.Position.WIDTH * Position.Position.HEIGHT:
            self.game_over = True
            self.draw_board()
            self.show_message("Draw!")

        self.current_player = 1  
    
    def show_message(self, text):
        pygame.draw.rect(self.screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
        label = self.font.render(text, True, WHITE)
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 40))
        pygame.display.update()
        pygame.time.wait(3000)
    
    def reset_game(self):
        self.position = Position.Position()
        self.game_over = False
        self.current_player = 1
    
    def return_to_menu(self):
        self.game_mode = None
    
    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.game_mode is None:  # Trạng thái menu
                    self.pvp_button.check_hover(mouse_pos)
                    self.pvc_button.check_hover(mouse_pos)
                    self.quit_button.check_hover(mouse_pos)
                    
                    if self.pvp_button.is_clicked(mouse_pos, event):
                        self.game_mode = 'pvp'
                        self.setup_game()
                    elif self.pvc_button.is_clicked(mouse_pos, event):
                        self.game_mode = 'pvc'
                        self.setup_game()
                    elif self.quit_button.is_clicked(mouse_pos, event):
                        pygame.quit()
                        sys.exit()
                else:  # Trạng thái game
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                        if (self.game_mode == 'pvc' and self.current_player == 1):                                
                            posx = event.pos[0]
                            col = posx // SQUARESIZE
                            if (self.position.can_play(col)):
                                self.handle_human_move(col)
                            else:
                                self.show_message("Column full! Pick another one.")
                                break
                            if not self.game_over:
                                self.draw_board()
                                self.clock.tick(60)
                        else: 
                            posx = event.pos[0]
                            col = posx // SQUARESIZE
                            if (self.position.can_play(col)):
                                self.handle_human_move(col)
                            else:
                                self.show_message("Column full! Pick another one.")
                                break
                            if not self.game_over:
                                self.draw_board()
                                self.clock.tick(60)

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:  # Nhấn R để chơi lại
                            self.reset_game()
                        elif event.key == pygame.K_m:  # Nhấn M để về menu
                            self.return_to_menu()
                        elif event.key == pygame.K_q:  # Nhấn Q để thoát
                            pygame.quit()
                            sys.exit()

            if self.game_mode is None:
                self.draw_menu()
            else :
                if not self.game_over and self.game_mode == 'pvc' and self.current_player == 2:
                    self.ai_move()
                
                if not self.game_over:
                    self.draw_board()
                    self.clock.tick(60)