import numpy as np
import math

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def next_prime(n: int) -> int:
    while not is_prime(n):
        n += 1
    return n

def log2(n: int) -> int:
    return 0 if n <= 1 else log2(n // 2) + 1

class TranspositionTable:
    def __init__(self, key_size: int = 64, value_size: int = 16, log_size: int = 20):
        """
        Khởi tạo bảng băm
        :param key_size: số bit của khóa (tối đa 64)
        :param value_size: số bit của giá trị (tối đa 64)
        :param log_size: log2 của kích thước bảng
        """
        assert key_size <= 64, "key_size quá lớn"
        assert value_size <= 64, "value_size quá lớn"
        assert log_size <= 64, "log_size quá lớn"

        self.key_size = key_size
        self.value_size = value_size
        self.log_size = log_size

        # Tính kích thước bảng (số nguyên tố)
        self.size = next_prime(1 << log_size)
        
        # Xác định kiểu dữ liệu phù hợp
        self.key_t = self._get_uint_type(key_size - log_size)
        self.value_t = self._get_uint_type(value_size)
        
        # Tạo mảng lưu trữ
        self.K = np.zeros(self.size, dtype=self.key_t)
        self.V = np.zeros(self.size, dtype=self.value_t)

    def _get_uint_type(self, bits: int) -> type:
        """Xác định kiểu numpy phù hợp cho số bit"""
        if bits <= 8:
            return np.uint8
        elif bits <= 16:
            return np.uint16
        elif bits <= 32:
            return np.uint32
        return np.uint64

    def index(self, key: int) -> int:
        """Hàm băm - trả về vị trí trong bảng"""
        return key % self.size

    def reset(self) -> None:
        """Đặt lại bảng về trạng thái ban đầu"""
        self.K.fill(0)
        self.V.fill(0)

    def put(self, key: int, value: int) -> None:
        """Thêm cặp key-value vào bảng"""
        assert key >> self.key_size == 0, "Key vượt quá kích thước bit quy định"
        assert value >> self.value_size == 0, "Value vượt quá kích thước bit quy định"
        
        pos = self.index(key)
        self.K[pos] = key  # Lưu key (có thể bị cắt bớt nếu key_t nhỏ hơn key_size)
        self.V[pos] = value

    def get(self, key: int) -> int:
        """Lấy giá trị từ bảng bằng key"""
        assert key >> self.key_size == 0, "Key vượt quá kích thước bit quy định"
        
        pos = self.index(key)
        return int(self.V[pos]) if self.K[pos] == (self.key_t)(key) else 0

    def __del__(self):
        """Hủy bảng khi đối tượng bị xóa"""
        if hasattr(self, 'K'):
            del self.K
        if hasattr(self, 'V'):
            del self.V