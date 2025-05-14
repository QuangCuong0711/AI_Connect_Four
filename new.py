import time
import Position
import Solver


def human_vs_ai():
    """Chế độ chơi người vs AI"""
    position = Position.Position()
    solver = Solver.Solver()
    
    while True:
        position.print_board()
        
        # Lượt người chơi
        if position.nb_moves() % 2 != 0:
            print("Lượt của bạn (X), nhập cột (1-7):")
            try:
                col = int(input()) - 1
                if col < 0 or col >= Position.Position.WIDTH:
                    print("Vui lòng nhập số từ 1 đến 7!")
                    continue
                if not position.can_play(col):
                    print("Cột này đã đầy!")
                    continue
                if position.is_winning_move(col):
                    position.playCol(col)
                    position.print_board()
                    print("Bạn đã thắng!")
                    break
                position.playCol(col)
            except ValueError:
                print("Vui lòng nhập số!")
                continue
        # Lượt AI
        else:
            print("AI đang suy nghĩ...")
            start_time = time.time()
            best_col = None
            best_score = -float('inf')
            
            # Kiểm tra nếu AI có thể thắng ngay
            for col in range(Position.Position.WIDTH):
                if position.can_play(col) and position.is_winning_move(col):
                    best_col = col
                    position.playCol(best_col)
                    position.print_board()
                    print("AI đã thắng!")
                    print(f"Thời gian suy nghĩ: {time.time() - start_time:.2f} giây")
                    return
            
            # Nếu không có nước thắng ngay, tìm nước tốt nhất
            for x in range(Position.Position.WIDTH):
                col = solver.column_order[x]
                if position.can_play(col):
                    P2 = Position.Position(position)
                    P2.playCol(col)
                    
                    # Kiểm tra nếu người chơi có thể thắng ở nước tiếp theo
                    opponent_can_win = False
                    for y in range(Position.Position.WIDTH):
                        if P2.can_play(y) and P2.is_winning_move(y):
                            opponent_can_win = True
                            break
                            
                    if opponent_can_win:
                        continue
                        
                    score = -solver.solve(P2)
                    if score > best_score or best_col is None:
                        best_col = col
                        best_score = score
            
            # Nếu không tìm được nước đi tốt, chọn nước đi hợp lệ đầu tiên
            if best_col is None:
                for col in range(Position.Position.WIDTH):
                    if position.can_play(col):
                        best_col = col
                        break
            
            position.playCol(best_col)
            end_time = time.time()
            print(f"Thời gian suy nghĩ: {end_time - start_time:.2f} giây")
            print(f"AI chọn cột {best_col+1}")
            
            # Kiểm tra nếu AI vừa thắng
            if position.is_winning_move(best_col):
                position.print_board()
                print("AI đã thắng!")
                return

if __name__ == "__main__":
    human_vs_ai()
