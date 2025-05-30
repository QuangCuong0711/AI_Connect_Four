from typing import Optional
from Position import Position

class OpeningBook:
    def __init__(self):
        self.book_file = "battles.txt"
        self.winning_sequences = {}
        self.load_from_file(self.book_file)

    def get_first_move(self):
        """Return the preferred first move (center column)"""
        return 3  # Column 4 (0-indexed)

    def find_next_move(self, position: Position, ai_player: int) -> Optional[int]:
        """Find the next move from the opening book"""
        current_sequence = position.get_played_sequence()
        if len(current_sequence) == 0 and ai_player == 1:
            return self.get_first_move()

        # Check battles.txt
        battle_move = self.check_battles_book(current_sequence, ai_player)
        if battle_move is not None and position.can_play(battle_move):
            print(f"Using battles.txt move: {battle_move}")
            return battle_move

        return None

    def check_battles_book(self, current_sequence: str, ai_player: int) -> Optional[int]:
        try:
            with open(self.book_file, "r") as file:
                for line_number, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        sequence, outcome = line.split(' ')
                        outcome = int(outcome)
                        if outcome not in {0, 1, 2}:
                            print(f"Warning: Invalid outcome {outcome} at line {line_number}, skipping")
                            continue
                        if not all(c in '1234567' for c in sequence):
                            print(f"Warning: Invalid sequence {sequence} at line {line_number}, skipping")
                            continue
                        if outcome not in {ai_player, 0}:  # Only consider AI win or draw
                            continue
                        if current_sequence == sequence[:len(current_sequence)] and len(sequence) > len(current_sequence):
                            next_move = int(sequence[len(current_sequence)]) - 1
                            return next_move
                    except ValueError as e:
                        print(f"Warning: Error parsing line {line_number} in {self.book_file}: {line} ({e}), skipping")
                        continue
                return None
        except IOError as e:
            print(f"Error reading {self.book_file}: {e}")
            return None

    def add_sequence(self, sequence: str, winner: int) -> None:
        """Add a winning sequence to the opening book"""
        if winner not in {0, 1, 2} or not all(c in '1234567' for c in sequence):
            print(f"Warning: Invalid sequence {sequence} or winner {winner}")
            return
        position = Position()
        try:
            for move in sequence:
                col = int(move) - 1
                if not position.can_play(col):
                    print(f"Warning: Invalid move in sequence {sequence}")
                    return
                position.playCol(col)
            if winner == 1 and not position.check_win(position.current_position):
                print(f"Warning: Sequence {sequence} does not lead to Player 1 win")
                return
            if winner == 2 and not position.check_win(position.mask & ~position.current_position):
                print(f"Warning: Sequence {sequence} does not lead to Player 2 win")
                return
        except ValueError as e:
            print(f"Warning: Invalid sequence {sequence}: {e}")
            return
        self.winning_sequences[sequence] = {"winner": winner}
        self.save_to_file(self.book_file)

    def remove_sequence(self, sequence: str) -> bool:
        """Remove a sequence from the opening book"""
        if sequence in self.winning_sequences:
            del self.winning_sequences[sequence]
            self.save_to_file(self.book_file)
            return True
        return False

    def get_all_sequences(self) -> dict:
        """Return all winning sequences in the opening book"""
        return self.winning_sequences

    def load_from_file(self, filename: str) -> bool:
        """Load opening book from file, skipping invalid lines"""
        self.book_file = filename
        self.winning_sequences = {}  # Reset winning sequences before loading
        try:
            with open(filename, 'r') as f:
                for line_number, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        sequence, winner = line.split(' ')
                        winner = int(winner)
                        if winner not in {0, 1, 2}:
                            print(f"Warning: Invalid winner {winner} at line {line_number}, skipping")
                            continue
                        if not all(c in '1234567' for c in sequence):
                            print(f"Warning: Invalid sequence {sequence} at line {line_number}, skipping")
                            continue
                        self.winning_sequences[sequence] = {"winner": winner}
                    except ValueError as e:
                        print(f"Warning: Error parsing line {line_number} in {filename}: {line} ({e}), skipping")
                        continue
            print(f"Loaded {len(self.winning_sequences)} sequences from {filename}")
            return True
        except IOError as e:
            print(f"Error loading {filename}: {e}")
            return False

    def save_to_file(self, filename: str) -> bool:
        """Save opening book to file"""
        try:
            with open(filename, 'w') as f:
                f.write("# Connect Four Opening Book\n")
                f.write("# Format: sequence winner\n")
                f.write("# sequence: string of column numbers (1-indexed)\n")
                f.write("# winner: 1 for Player 1, 2 for Player 2, 0 for draw\n\n")
                for sequence, data in self.winning_sequences.items():
                    f.write(f"{sequence} {data['winner']}\n")
            return True
        except IOError as e:
            print(f"Error saving {filename}: {e}")
            return False