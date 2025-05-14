import numpy as np
import Position

class MoveSorter:
    def __init__(self):
        self.size = 0
        self.entries = np.zeros(Position.Position.WIDTH, dtype=[('move', 'u8'), ('score', 'i4')])
    
    def add(self, move: int, score: int) -> None:
        if self.size >= len(self.entries):
            return
            
        pos = self.size
        while pos > 0 and self.entries[pos-1]['score'] > score:
            if pos < len(self.entries):  # Thêm điều kiện kiểm tra
                self.entries[pos] = self.entries[pos-1]
            pos -= 1
        
        if pos < len(self.entries):  # Thêm điều kiện kiểm tra
            self.entries[pos]['move'] = move
            self.entries[pos]['score'] = score
        self.size += 1
    
    def get_next(self) -> int:
        if self.size > 0:
            self.size -= 1
            return int(self.entries[self.size]['move'])
        return 0
    
    def reset(self) -> None:
        self.size = 0
    
    def __len__(self) -> int:
        return self.size