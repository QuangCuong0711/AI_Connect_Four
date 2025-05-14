import struct

class OpeningBook:
    def __init__(self, book_file=None):
        self.width = 7
        self.height = 6
        self.depth = -1
        self.book = {}
        if book_file:
            self.load_book(book_file)
    
    def load_book(self, filename):
        try:
            with open(filename, 'rb') as f:
                # Đọc header (6 bytes)
                header = f.read(6)
                if len(header) != 6:
                    raise ValueError("Invalid header size")
                
                width, height, depth, key_bytes, value_bytes, log_size = struct.unpack('BBBBBB', header)
                
                # Validate header
                if width != self.width or height != self.height:
                    raise ValueError(f"Invalid board size in book: {width}x{height}, expected 7x6")
                
                if depth > self.width * self.height:
                    raise ValueError(f"Invalid depth in book: {depth}")
                
                if key_bytes > 8 or value_bytes != 1:
                    raise ValueError(f"Invalid key/value size: key={key_bytes}, value={value_bytes}")
                
                # Tính toán kích thước dữ liệu
                size = self._next_prime(1 << log_size)
                key_size = size * key_bytes
                value_size = size * value_bytes
                
                # Đọc keys và values
                keys = f.read(key_size)
                values = f.read(value_size)
                
                if len(keys) != key_size or len(values) != value_size:
                    raise ValueError("Invalid data size")
                
                # Xử lý dữ liệu tùy thuộc vào key_bytes
                if key_bytes == 4:
                    fmt = f'<{size}I'  # unsigned int 32-bit
                elif key_bytes == 8:
                    fmt = f'<{size}Q'  # unsigned long long 64-bit
                else:
                    raise ValueError(f"Unsupported key size: {key_bytes} bytes")
                
                keys = struct.unpack(fmt, keys)
                values = struct.unpack(f'{size}B', values)  # values là 1 byte mỗi entry
                
                # Tạo dictionary để tra cứu nhanh
                self.book = {k: v for k, v in zip(keys, values) if v != 0}
                self.depth = depth
                
                print(f"Loaded opening book with {len(self.book)} positions (max depth: {self.depth})")
                
        except Exception as e:
            print(f"Error loading opening book: {e}")
            self.book = {}
            self.depth = -1
    
    def _next_prime(self, n):
        """Tìm số nguyên tố nhỏ nhất >= n"""
        if n <= 2:
            return 2
        if n % 2 == 0:
            n += 1
        while not self._is_prime(n):
            n += 2
        return n
    
    def _is_prime(self, n):
        """Kiểm tra số nguyên tố"""
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
    
    def get(self, position):
        """Lấy nước đi từ opening book nếu có"""
        if position.nb_moves() > self.depth:
            return None
        
        key = position.key3()
        move = self.book.get(key)
        if move is not None and move != 0:
            return move - 1  # Chuyển từ 1-7 sang 0-6
        return None