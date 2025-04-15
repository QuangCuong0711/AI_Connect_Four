import sys
import struct
from typing import List, Dict, Tuple, Optional
from functools import lru_cache
from Position import Position
from TranspositionTable import TranspositionTable

class OpeningBook:
    def __init__(self, width: int = Position.WIDTH, height: int = Position.HEIGHT):
        self.width = width
        self.height = height
        self.depth = -1
        self.table = None

    def load(self, filename: str) -> bool:
        """Load opening book from a binary file. Returns True if successful."""
        try:
            with open(filename, 'rb') as f:
                _width = struct.unpack('B', f.read(1))[0]
                _height = struct.unpack('B', f.read(1))[0]
                _depth = struct.unpack('B', f.read(1))[0]
                key_bytes = struct.unpack('B', f.read(1))[0]
                value_bytes = struct.unpack('B', f.read(1))[0]
                log_size = struct.unpack('B', f.read(1))[0]

                if (_width != self.width or _height != self.height or 
                    _depth > self.width * self.height or key_bytes > 8 or value_bytes != 1):
                    print("Invalid opening book format")
                    return False

                self.table = TranspositionTable(key_bytes, value_bytes, log_size)
                f.readinto(self.table.keys)
                f.readinto(self.table.values)
                self.depth = _depth
                print(f"Loaded opening book with depth {self.depth}")
                return True
        except Exception as e:
            print(f"Error loading opening book: {e}")
            self.table = None
            self.depth = -1
            return False

    def get(self, position: Position) -> int:
        """Get the best move for the given position from the opening book.
        Returns the column (0-6) or -1 if not found."""
        if self.depth < 0 or not self.table or position.moves > self.depth:
            return -1
        
        try:
            return self.table.get(position.key3())
        except (AttributeError, Exception) as e:
            print(f"Error retrieving from opening book: {e}")
            return -1