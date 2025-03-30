import sys
import struct
from typing import List, Dict, Tuple, Optional
from functools import lru_cache
from MoveSorter import MoveSorter
from Position import Position
from OpeningBook import OpeningBook
from Solver import Solver
from TranspositionTable import TranspositionTable

def main():
    solver = Solver()
    weak = False
    analyze = False
    opening_book = "7x6.book"

    for i in range(1, len(sys.argv)):
        if sys.argv[i][0] == '-':
            if sys.argv[i][1] == 'w':
                weak = True
            elif sys.argv[i][1] == 'b' and i+1 < len(sys.argv):
                opening_book = sys.argv[i+1]
                i += 1
            elif sys.argv[i][1] == 'a':
                analyze = True

    solver.load_book(opening_book)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        position = Position()
        moves_played = position.play_sequence(line)
        if moves_played != len(line):
            print(f"Invalid move {moves_played + 1} in sequence: {line}")
            continue

        if analyze:
            scores = solver.analyze(position, weak)
            print(" ".join(map(str, scores)))
        else:
            score = solver.solve(position, weak)
            print(score)


if __name__ == "__main__":
    main()