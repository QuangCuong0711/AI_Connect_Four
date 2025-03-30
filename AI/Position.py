import sys
import struct
from typing import List, Dict, Tuple, Optional
from functools import lru_cache

class Position:
    WIDTH = 7
    HEIGHT = 6
    MIN_SCORE = -(WIDTH * HEIGHT) // 2 + 3
    MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3

    def __init__(self, current_position: int = 0, mask: int = 0, moves: int = 0):
        self.current_position = current_position
        self.mask = mask
        self.moves = moves

    @staticmethod
    def bottom_mask_col(col: int) -> int:
        return 1 << (col * (Position.HEIGHT + 1))

    @staticmethod
    def top_mask_col(col: int) -> int:
        return 1 << ((Position.HEIGHT - 1) + col * (Position.HEIGHT + 1))

    @staticmethod
    def column_mask(col: int) -> int:
        return ((1 << Position.HEIGHT) - 1) << (col * (Position.HEIGHT + 1))

    @staticmethod
    def bottom_mask() -> int:
        mask = 0
        for col in range(Position.WIDTH):
            mask |= Position.bottom_mask_col(col)
        return mask

    @staticmethod
    def board_mask() -> int:
        return Position.bottom_mask() * ((1 << Position.HEIGHT) - 1)

    def can_play(self, col: int) -> bool:
        return (self.mask & Position.top_mask_col(col)) == 0

    def play(self, move: int) -> None:
        self.current_position ^= self.mask
        self.mask |= move
        self.moves += 1

    def play_col(self, col: int) -> None:
        self.play((self.mask + Position.bottom_mask_col(col)) & Position.column_mask(col))

    def play_sequence(self, sequence: str):
        for char in sequence:
            if char.isdigit():
                col = int(char) - 1
                self.play(col)
            else:
                print(f"WARNING: Ignoring invalid character '{char}' in move sequence.")
        return len(sequence)

    def is_winning_move(self, col: int) -> bool:
        return self.winning_position() & self.possible() & Position.column_mask(col)

    def can_win_next(self) -> bool:
        return self.winning_position() & self.possible()

    def possible(self) -> int:
        return (self.mask + Position.bottom_mask()) & Position.board_mask()

    def winning_position(self) -> int:
        return self.compute_winning_position(self.current_position, self.mask)

    def opponent_winning_position(self) -> int:
        return self.compute_winning_position(self.current_position ^ self.mask, self.mask)

    @staticmethod
    def compute_winning_position(position: int, mask: int) -> int:
        # Vertical
        r = (position << 1) & (position << 2) & (position << 3)

        # Horizontal
        p = (position << (Position.HEIGHT + 1)) & (position << 2 * (Position.HEIGHT + 1))
        r |= p & (position << 3 * (Position.HEIGHT + 1))
        r |= p & (position >> (Position.HEIGHT + 1))
        p = (position >> (Position.HEIGHT + 1)) & (position >> 2 * (Position.HEIGHT + 1))
        r |= p & (position << (Position.HEIGHT + 1))
        r |= p & (position >> 3 * (Position.HEIGHT + 1))

        # Diagonal 1
        p = (position << Position.HEIGHT) & (position << 2 * Position.HEIGHT)
        r |= p & (position << 3 * Position.HEIGHT)
        r |= p & (position >> Position.HEIGHT)
        p = (position >> Position.HEIGHT) & (position >> 2 * Position.HEIGHT)
        r |= p & (position << Position.HEIGHT)
        r |= p & (position >> 3 * Position.HEIGHT)

        # Diagonal 2
        p = (position << (Position.HEIGHT + 2)) & (position << 2 * (Position.HEIGHT + 2))
        r |= p & (position << 3 * (Position.HEIGHT + 2))
        r |= p & (position >> (Position.HEIGHT + 2))
        p = (position >> (Position.HEIGHT + 2)) & (position >> 2 * (Position.HEIGHT + 2))
        r |= p & (position << (Position.HEIGHT + 2))
        r |= p & (position >> 3 * (Position.HEIGHT + 2))

        return r & (Position.board_mask() ^ mask)

    def possible_non_losing_moves(self) -> int:
        assert not self.can_win_next()
        possible_mask = self.possible()
        opponent_win = self.opponent_winning_position()
        forced_moves = possible_mask & opponent_win
        
        if forced_moves:
            if forced_moves & (forced_moves - 1):
                return 0
            possible_mask = forced_moves
        
        return possible_mask & ~(opponent_win >> 1)

    def move_score(self, move: int) -> int:
        return bin(self.compute_winning_position(self.current_position | move, self.mask)).count('1')

    def key(self) -> int:
        return self.current_position + self.mask

    def key3(self) -> int:
        key_forward = 0
        for col in range(Position.WIDTH):
            key_forward = self.partial_key3(key_forward, col)

        key_reverse = 0
        for col in range(Position.WIDTH-1, -1, -1):
            key_reverse = self.partial_key3(key_reverse, col)

        return min(key_forward, key_reverse) // 3

    def partial_key3(self, key: int, col: int) -> int:
        pos = 1 << (col * (Position.HEIGHT + 1))
        while pos & self.mask:
            key *= 3
            if pos & self.current_position:
                key += 1
            else:
                key += 2
            pos <<= 1
        key *= 3
        return key

    def __str__(self) -> str:
        board = []
        for row in range(Position.HEIGHT-1, -1, -1):
            line = []
            for col in range(Position.WIDTH):
                mask = 1 << (col * (Position.HEIGHT + 1) + row)
                if self.mask & mask:
                    if self.current_position & mask:
                        line.append('X')
                    else:
                        line.append('O')
                else:
                    line.append('.')
            board.append(' '.join(line))
        return '\n'.join(board)