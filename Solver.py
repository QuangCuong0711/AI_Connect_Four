import numpy as np
import Position
import MoveSorter
import TranspositionTable

class Solver:
    def __init__(self, max_depth = 10):
        self.node_count = 0
        self.max_depth = max_depth  # Độ sâu tối đa (None = không giới hạn)
        self.column_order = [3, 2, 4, 1, 5, 0, 6]
        self.transposition_table = TranspositionTable.TranspositionTable(Position.Position.WIDTH*(Position.Position.HEIGHT + 1), self.log2(Position.Position.MAX_SCORE - Position.Position.MIN_SCORE + 1) + 1,23)  

    def log2(self, n):
        if n <= 1:
            return 0
        return int(np.log2(n/2) + 1)
    
    def evaluate(self, position):
        """
        Đánh giá vị trí hiện tại bằng cách đếm các hàng 4 tiềm năng
        Trả về điểm số: (số hàng tiềm năng của người chơi) - (số hàng tiềm năng của đối thủ)
        """
        # Kiểm tra nếu có người thắng
        if position.is_winning_move(0):  # Giả sử 0 là cột đầu tiên, cần kiểm tra tất cả cột
            for col in range(Position.Position.WIDTH):
                if position.is_winning_move(col):
                    return float('inf') if position.nb_moves() % 2 == 1 else float('-inf')
        
        # Tính số hàng 4 tiềm năng cho mỗi người chơi
        def count_potential_fours(pos, mask):
            count = 0
            
            # Kiểm tra hàng ngang (7 vị trí × 4 cách)
            for y in range(Position.Position.HEIGHT):
                for x in range(Position.Position.WIDTH - 3):
                    window = 0
                    for i in range(4):
                        bit_pos = (x + i) * (Position.Position.HEIGHT + 1) + y
                        if not (mask & (1 << bit_pos)):
                            window = -1  # Có ô trống trong cửa sổ
                            break
                    if window != -1:
                        count += 1
            
            # Kiểm tra hàng dọc (4 vị trí × 7 cách)
            for x in range(Position.Position.WIDTH):
                for y in range(Position.Position.HEIGHT - 3):
                    window = 0
                    for i in range(4):
                        bit_pos = x * (Position.Position.HEIGHT + 1) + y + i
                        if not (mask & (1 << bit_pos)):
                            window = -1
                            break
                    if window != -1:
                        count += 1
            
            # Kiểm tra chéo lên (4 vị trí × 4 cách)
            for x in range(Position.Position.WIDTH - 3):
                for y in range(Position.Position.HEIGHT - 3):
                    window = 0
                    for i in range(4):
                        bit_pos = (x + i) * (Position.Position.HEIGHT + 1) + y + i
                        if not (mask & (1 << bit_pos)):
                            window = -1
                            break
                    if window != -1:
                        count += 1
            
            # Kiểm tra chéo xuống (4 vị trí × 4 cách)
            for x in range(Position.Position.WIDTH - 3):
                for y in range(3, Position.Position.HEIGHT):
                    window = 0
                    for i in range(4):
                        bit_pos = (x + i) * (Position.Position.HEIGHT + 1) + y - i
                        if not (mask & (1 << bit_pos)):
                            window = -1
                            break
                    if window != -1:
                        count += 1
            
            return count
        
        # Số hàng tiềm năng cho người chơi hiện tại và đối thủ
        current_player = position.current_position ^ position.mask
        opponent = position.current_position
        
        current_potential = count_potential_fours(current_player, position.mask)
        opponent_potential = count_potential_fours(opponent, position.mask)
        
        return current_potential - opponent_potential

    def negamax(self, P, alpha, beta, depth=0):
        assert alpha < beta
        self.node_count += 1

        # Kiểm tra điều kiện dừng theo độ sâu
        if self.max_depth is not None and depth >= self.max_depth:
            return self.evaluate(P)

        possible = P.possible_Non_Losing_Moves()
        if possible == 0:
            return -(Position.Position.WIDTH * Position.Position.HEIGHT - P.nb_moves()) // 2
        if P.nb_moves() == Position.Position.WIDTH * Position.Position.HEIGHT - 2:
            return 0

        min_score = -(Position.Position.WIDTH*Position.Position.HEIGHT-2 - P.nb_moves())//2
        if alpha < min_score:
            alpha = min_score
            if alpha >= beta:
                return alpha

        max_score = (Position.Position.WIDTH * Position.Position.HEIGHT - 1 - P.nb_moves()) // 2
        if beta > max_score:
            beta = max_score
            if alpha >= beta:
                return beta

        key = P.key()
        val = self.transposition_table.get(key)
        if val:
            if val > Position.Position.MAX_SCORE - Position.Position.MIN_SCORE + 1:  # lower bound
                min_val = val + 2*Position.Position.MIN_SCORE - Position.Position.MAX_SCORE - 2
                if alpha < min_val:
                    alpha = min_val
                    if alpha >= beta:
                        return alpha
            else:  # upper bound
                max_val = val + Position.Position.MIN_SCORE - 1
                if beta > max_val:
                    beta = max_val
                    if alpha >= beta:
                        return beta

        moves = MoveSorter.MoveSorter()
        for i in reversed(range(Position.Position.WIDTH)):
            move = possible & Position.Position.column_mask(self.column_order[i])
            if move != 0:
                moves.add(move, P.moveScore(move))

        best_score = -float('inf')
        while True:
            next_move = moves.get_next()
            if next_move == 0:
                break

            P2 = Position.Position(P)
            P2.play(next_move)
            score = -self.negamax(P2, -beta, -alpha, depth + 1)

            if score >= beta:
                # Đảm bảo giá trị nằm trong phạm vi cho phép trước khi lưu
                value_to_store = score + Position.Position.MAX_SCORE - 2*Position.Position.MIN_SCORE + 2
                max_allowed = (1 << self.transposition_table.value_size) - 1
                if value_to_store > max_allowed:
                    value_to_store = max_allowed
                elif value_to_store < 0:
                    value_to_store = 0
                self.transposition_table.put(key, value_to_store)
                return score

            if score > best_score:
                best_score = score
                if score > alpha:
                    alpha = score

        # Đảm bảo giá trị nằm trong phạm vi cho phép trước khi lưu
        value_to_store = alpha - Position.Position.MIN_SCORE + 1
        max_allowed = (1 << self.transposition_table.value_size) - 1
        if value_to_store > max_allowed:
            value_to_store = max_allowed
        elif value_to_store < 0:
            value_to_store = 0
        self.transposition_table.put(key, value_to_store)
        
        return best_score
    def solve(self, P, weak=False):

        if P.canWinNext():
            return (Position.Position.WIDTH * Position.Position.HEIGHT + 1 - P.nb_moves()) // 2

        min_score = -(Position.Position.WIDTH * Position.Position.HEIGHT - P.nb_moves()) // 2
        max_score = (Position.Position.WIDTH * Position.Position.HEIGHT + 1 - P.nb_moves()) // 2

        if weak:
            min_score = -1
            max_score = 1

        while min_score < max_score:
            med = min_score + (max_score - min_score) // 2

            # Điều chỉnh điểm giữa để ưu tiên test vùng gần 0
            if med <= 0 and min_score // 2 < med:
                med = min_score // 2
            elif med >= 0 and max_score // 2 > med:
                med = max_score // 2

            # Dùng null-window để kiểm tra xem điểm thực tế lớn hơn hay nhỏ hơn `med`
            score = self.negamax(P, med, med + 1)

            if score <= med:
                max_score = score
            else:
                min_score = score

        return min_score

    def set_max_depth(self, depth):
        """Thiết lập độ sâu tối đa cho thuật toán"""
        self.max_depth = depth