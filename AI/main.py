import sys
import struct
import numpy as np
import random
import pickle
from collections import defaultdict
import time
from typing import List, Dict, Tuple, Optional
from functools import lru_cache
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from MoveSorter import MoveSorter
from Position import Position
from Solver import Solver
from TranspositionTable import TranspositionTable

def play_vs_ai(solver: Solver):
    position = Position()
    human_turn = True  # True for human's turn, False for AI's turn
    
    print("Connect Four - Human (O) vs AI (X)")
    print("Nhập số cột (1-7) để chơi\n")
    
    while True:
        print(position)
        
        # Check for draw
        if position.moves == Position.WIDTH * Position.HEIGHT:
            print("Hòa!")
            break
            
        if human_turn:
            # Human's turn
            while True:
                try:
                    col = int(input("Lượt bạn (1-7): ")) - 1
                    if 0 <= col < Position.WIDTH and position.can_play(col):
                        if position.is_winning_move(col):
                            position.play_col(col)
                            print(position)
                            print("Bạn thắng! Xuất sắc!")
                            return
                        position.play_col(col)
                        break
                    print("Cột không hợp lệ hoặc đã đầy!")
                except ValueError:
                    print("Vui lòng nhập số từ 1-7")
        else:
            # AI's turn
            print("\nAI đang suy nghĩ...")

            # If no book move available, use the solver analysis
            scores = solver.analyze(position)
                
            # Find the best move
            best_col = -1
            best_score = -float('inf')
                
            for col in range(Position.WIDTH):
                if position.can_play(col) and scores[col] > best_score:
                    best_score = scores[col]
                    best_col = col
            
            if best_col != -1:
                print(f"AI chọn cột {best_col + 1}")
                
                if position.is_winning_move(best_col):
                    position.play_col(best_col)
                    print(position)
                    print("AI thắng! Hãy thử lại!")
                    return
                    
                position.play_col(best_col)
            else:
                print("AI không tìm được nước đi hợp lệ!")
                return
        
        human_turn = not human_turn

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[int]

class AIResponse(BaseModel):
    move: int

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo solver cho API
api_solver = Solver()

@app.post("/api/connect4-move")
async def make_move(game_state: GameState) -> AIResponse:
    try:
        if not game_state.valid_moves:
            raise ValueError("Không có nước đi hợp lệ")
            
        # Chuyển đổi dữ liệu từ API thành Position
        position = Position()
        position.from_2d_array(game_state.board)
        
        # Thử lấy nước đi từ opening book trước
        book_move = api_solver.get_book_move(position)
        if book_move is not None and book_move in game_state.valid_moves:
            return AIResponse(move=book_move)
        
        # Phân tích vị trí và chọn nước đi tốt nhất
        scores = api_solver.analyze(position)
        
        # Tìm nước đi tốt nhất từ danh sách nước đi hợp lệ
        best_move = -1
        best_score = -float('inf')
        
        for col in game_state.valid_moves:
            if scores[col] > best_score:
                best_score = scores[col]
                best_move = col
        
        # Nếu không tìm được nước đi tốt nhất, chọn một nước đi ngẫu nhiên
        if best_move == -1 and game_state.valid_moves:
            best_move = random.choice(game_state.valid_moves)
            
        return AIResponse(move=best_move)
    except Exception as e:
        if game_state.valid_moves:
            return AIResponse(move=game_state.valid_moves[0])
        raise HTTPException(status_code=400, detail=str(e))

def main():
    solver = Solver()
    weak = False
    analyze = False
    interactive = False
    args = sys.argv[1:]
    input_from_stdin = False
    api_mode = False
    opening_book_file = None
    
    for i, arg in enumerate(args):
        if arg == '-i':
            interactive = True
        elif arg == '-w':
            weak = True
        elif arg == '-a':
            analyze = True
        elif arg == '-api':
            api_mode = True
        elif arg == '-b':
            if i+1 < len(args) and not args[i+1].startswith('-'):
                opening_book_file = args[i+1]
                print(f"Using opening book: {opening_book_file}")
        elif not arg.startswith('-') and not arg.isdigit():
            input_from_stdin = True

    # Load opening book if specified
    if opening_book_file:
        if solver.load_opening_book(opening_book_file):
            print("Opening book loaded successfully")
        else:
            print("Failed to load opening book")

    if interactive:
        play_vs_ai(solver)
        return
    
    if api_mode:
        print("Khởi động API Connect Four AI trên cổng 8080...")
        uvicorn.run(app, host="0.0.0.0", port=8080)
        return
    
    if not sys.stdin.isatty() and input_from_stdin:
        for line in sys.stdin:
            line = line.strip()
            if line:
                position = Position()
                try:
                    position.play_sequence(line)
                    if analyze:
                        scores = solver.analyze(position, weak)
                        print(" ".join(map(str, scores)))
                    else:
                        score = solver.solve(position, weak)
                        print(score)
                except ValueError as e:
                    print(f"Lỗi khi xử lý nước đi: {e}")
    else:
        print("Sử dụng các tùy chọn sau:")
        print("  -i: Chơi với AI")
        print("  -api: Khởi động API Connect Four AI")
        print("  -b [file]: Sử dụng opening book từ file")
        print("  -w: Giảm độ mạnh của solver")
        print("  -a: Phân tích vị trí")

if __name__ == "__main__":
    main()