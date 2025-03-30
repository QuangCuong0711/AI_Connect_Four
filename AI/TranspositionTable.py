import sys
import struct
from typing import List, Dict, Tuple, Optional
from functools import lru_cache

class TranspositionTable:
    def __init__(self, key_size: int = 8, value_size: int = 1, log_size: int = 24):
        self.size = self.next_prime(1 << log_size)
        self.keys = bytearray(self.size * key_size)
        self.values = bytearray(self.size * value_size)
        self.key_size = key_size
        self.value_size = value_size

    @staticmethod
    def next_prime(n: int) -> int:
        if n < 2:
            return 2
        if n % 2 == 0:
            n += 1
        while True:
            if TranspositionTable.is_prime(n):
                return n
            n += 2

    @staticmethod
    def is_prime(n: int) -> bool:
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def index(self, key: int) -> int:
        return key % self.size

    def put(self, key: int, value: int) -> None:
        idx = self.index(key)
        start = idx * self.key_size
        self.keys[start:start+self.key_size] = key.to_bytes(self.key_size, 'little')
        start = idx * self.value_size
        self.values[start:start+self.value_size] = value.to_bytes(self.value_size, 'little')

    def get(self, key: int) -> int:
        idx = self.index(key)
        start = idx * self.key_size
        stored_key = int.from_bytes(self.keys[start:start+self.key_size], 'little')
        if stored_key == key:
            start = idx * self.value_size
            return int.from_bytes(self.values[start:start+self.value_size], 'little')
        return 0