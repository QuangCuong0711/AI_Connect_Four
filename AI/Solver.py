from MoveSorter import MoveSorter
from Position import Position
from OpeningBook import OpeningBook
from TranspositionTable import TranspositionTable

class Solver:
    INVALID_MOVE = -1000

    def __init__(self):
        self.transposition_table = TranspositionTable()
        self.book = OpeningBook()
        self.node_count = 0
        self.column_order = [Position.WIDTH // 2 + (1 - 2 * (i % 2)) * (i + 1) // 2 
                            for i in range(Position.WIDTH)]

    def negamax(self, position: Position, alpha: int, beta: int) -> int:
        assert alpha < beta
        assert not position.can_win_next()

        self.node_count += 1

        possible = position.possible_non_losing_moves()
        if possible == 0:
            return -(Position.WIDTH * Position.HEIGHT - position.moves) // 2

        if position.moves >= Position.WIDTH * Position.HEIGHT - 2:
            return 0

        min_score = -(Position.WIDTH * Position.HEIGHT - 2 - position.moves) // 2
        if alpha < min_score:
            alpha = min_score
            if alpha >= beta:
                return alpha

        max_score = (Position.WIDTH * Position.HEIGHT - 1 - position.moves) // 2
        if beta > max_score:
            beta = max_score
            if alpha >= beta:
                return beta

        key = position.key()
        val = self.transposition_table.get(key)
        if val:
            if val > Position.MAX_SCORE - Position.MIN_SCORE + 1:
                min_score = val + 2 * Position.MIN_SCORE - Position.MAX_SCORE - 2
                if alpha < min_score:
                    alpha = min_score
                    if alpha >= beta:
                        return alpha
            else:
                max_score = val + Position.MIN_SCORE - 1
                if beta > max_score:
                    beta = max_score
                    if alpha >= beta:
                        return beta

        book_val = self.book.get(position)
        if book_val:
            return book_val + Position.MIN_SCORE - 1

        move_sorter = MoveSorter()
        for col in self.column_order:
            move = possible & Position.column_mask(col)
            if move:
                move_sorter.add(move, position.move_score(move))

        best_score = -Position.WIDTH * Position.HEIGHT
        while True:
            move = move_sorter.get_next()
            if not move:
                break
            
            new_position = Position(position.current_position, position.mask, position.moves)
            new_position.play(move)
            score = -self.negamax(new_position, -beta, -alpha)

            if score >= beta:
                self.transposition_table.put(key, score + Position.MAX_SCORE - 2 * Position.MIN_SCORE + 2)
                return score
            if score > alpha:
                alpha = score
                best_score = score

        self.transposition_table.put(key, alpha - Position.MIN_SCORE + 1)
        return best_score

    def solve(self, position: Position, weak: bool = False) -> int:
        if position.can_win_next():
            return (Position.WIDTH * Position.HEIGHT + 1 - position.moves) // 2

        min_score = -(Position.WIDTH * Position.HEIGHT - position.moves) // 2
        max_score = (Position.WIDTH * Position.HEIGHT + 1 - position.moves) // 2

        if weak:
            min_score = -1
            max_score = 1

        while min_score < max_score:
            med = min_score + (max_score - min_score) // 2
            if med <= 0 and min_score // 2 < med:
                med = min_score // 2
            elif med >= 0 and max_score // 2 > med:
                med = max_score // 2
            
            score = self.negamax(position, med, med + 1)
            if score <= med:
                max_score = score
            else:
                min_score = score

        return min_score

    def analyze(self, position: Position, weak: bool = False) -> list[int]:
        scores = [Solver.INVALID_MOVE] * Position.WIDTH
        for col in range(Position.WIDTH):
            if position.can_play(col):
                if position.is_winning_move(col):
                    scores[col] = (Position.WIDTH * Position.HEIGHT + 1 - position.moves) // 2
                else:
                    new_position = Position(position.current_position, position.mask, position.moves)
                    new_position.play_col(col)
                    scores[col] = -self.solve(new_position, weak)
        return scores

    def load_book(self, book_file: str) -> None:
        self.book.load(book_file)

    def reset(self) -> None:
        self.node_count = 0
        self.transposition_table = TranspositionTable()