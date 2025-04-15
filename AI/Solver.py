from typing import List, Optional
from Position import Position
from MoveSorter import MoveSorter
from TranspositionTable import TranspositionTable

class Solver:
    """
    Connect 4 solver using Negamax algorithm with alpha-beta pruning
    and various optimization techniques.
    """
    INVALID_MOVE = -1000

    def __init__(self):
        """Initialize the solver"""
        self.node_count = 0
        self.trans_table = {}  # Use an empty dict as transposition table
        
        # Initialize column order for exploration (center columns first)
        self.column_order = []
        for i in range(Position.WIDTH):
            self.column_order.append(Position.WIDTH // 2 + (1 - 2 * (i % 2)) * (i + 1) // 2)
        # For WIDTH=7: column_order = [3, 4, 2, 5, 1, 6, 0]

    def load_book(self, book_file: str) -> None:
        """Load opening book from file"""
        # Implementation would depend on the book file format
        try:
            with open(book_file, 'r') as f:
                # Simple implementation - actual parsing would depend on format
                for line in f:
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            key = int(parts[0])
                            value = int(parts[1])
                            self.opening_book[key] = value
        except Exception as e:
            print(f"Error loading opening book: {e}")

    def negamax(self, position: Position, alpha: int, beta: int) -> int:

        assert alpha < beta
        assert not position.can_win_next()
        
        self.node_count += 1  # Increment counter of explored nodes
        
        # Check if there are valid moves
        possible = position.possible_non_losing_moves()
        if possible == 0:  # No possible non-losing moves, opponent wins next move
            return -((Position.WIDTH * Position.HEIGHT - position.nb_moves()) // 2)
        
        # Check for draw game
        if position.nb_moves() >= Position.WIDTH * Position.HEIGHT - 2:
            return 0
        
        # Lower bound of score as opponent cannot win next move
        min_score = -((Position.WIDTH * Position.HEIGHT - 2 - position.nb_moves()) // 2)
        if alpha < min_score:
            alpha = min_score
            if alpha >= beta:
                return alpha  # Prune if window is empty
        
        # Upper bound of our score as we cannot win immediately
        max_score = (Position.WIDTH * Position.HEIGHT - 1 - position.nb_moves()) // 2
        if beta > max_score:
            beta = max_score
            if alpha >= beta:
                return beta  # Prune if window is empty
        
        # Check transposition table
        key = position.key()
        val = self.trans_table.get(key)
        if val is not None:
            if val > Position.MAX_SCORE - Position.MIN_SCORE + 1:  # We have a lower bound
                min_val = val + 2 * Position.MIN_SCORE - Position.MAX_SCORE - 2
                if alpha < min_val:
                    alpha = min_val
                    if alpha >= beta:
                        return alpha  # Prune if window is empty
            else:  # We have an upper bound
                max_val = val + Position.MIN_SCORE - 1
                if beta > max_val:
                    beta = max_val
                    if alpha >= beta:
                        return beta  # Prune if window is empty
        
        # Check opening book (if implemented)
        # book_val = self.book.get(position)
        # if book_val is not None:
        #     return book_val + Position.MIN_SCORE - 1
        
        # Sort moves
        moves = []
        for i in range(Position.WIDTH - 1, -1, -1):
            col = self.column_order[i]
            move = possible & Position.column_mask(col)
            if move:
                # Add (move, score) pair to moves list
                moves.append((move, position.move_score(move)))
        
        # Sort moves by score
        moves.sort(key=lambda x: x[1], reverse=True)
        
        for move, _ in moves:
            new_pos = Position(position)
            new_pos.play(move)
            score = -self.negamax(new_pos, -beta, -alpha)
            
            if score >= beta:
                # Save lower bound
                self.trans_table[key] = score + Position.MAX_SCORE - 2 * Position.MIN_SCORE + 2
                return score  # Prune
            
            if score > alpha:
                alpha = score  # Reduce window for next exploration
        
        # Save upper bound
        self.trans_table[key] = alpha - Position.MIN_SCORE + 1
        return alpha

    def solve(self, position: Position, weak: bool = False) -> int:
        # Check for immediate win
        if position.can_win_next():
            return (Position.WIDTH * Position.HEIGHT + 1 - position.nb_moves()) // 2
        
        # Initialize min-max bounds
        min_score = -(Position.WIDTH * Position.HEIGHT - position.nb_moves()) // 2
        max_score = (Position.WIDTH * Position.HEIGHT + 1 - position.nb_moves()) // 2
        
        if weak:
            min_score = -1
            max_score = 1
        
        # Iteratively narrow the min-max exploration window
        while min_score < max_score:
            med = min_score + (max_score - min_score) // 2
            
            # Adjust median for better performance
            if med <= 0 and min_score // 2 < med:
                med = min_score // 2
            elif med >= 0 and max_score // 2 > med:
                med = max_score // 2
                
            # Use a null depth window to determine if score is greater or smaller than med
            r = self.negamax(position, med, med + 1)
            
            if r <= med:
                max_score = r
            else:
                min_score = r
                
        return min_score

    def analyze(self, position: Position, weak: bool = False) -> List[int]:
        """
        Analyze all possible moves from a position.
        
        Args:
            position: Position to analyze
            weak: If true, only distinguish between win/draw/loss
            
        Returns:
            List of scores for each column, INVALID_MOVE for invalid moves
        """
        scores = [self.INVALID_MOVE] * Position.WIDTH
        
        # Check each column
        for col in range(Position.WIDTH):
            if position.can_play(col):
                if position.is_winning_move(col):
                    scores[col] = (Position.WIDTH * Position.HEIGHT + 1 - position.nb_moves()) // 2
                else:
                    # Create new position with this move
                    new_pos = Position(position)
                    new_pos.play_col(col)
                    scores[col] = -self.solve(new_pos, weak)
        
        return scores

    def reset(self) -> None:
        """Reset the solver state"""
        self.node_count = 0
        self.trans_table = {}

    def get_node_count(self) -> int:
        """Get number of nodes explored in the last search"""
        return self.node_count