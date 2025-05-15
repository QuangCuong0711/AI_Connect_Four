# 🎮 Connect Four Game Project
Dự án này là trò chơi Connect Four (4-in-a-row) được xây dựng bằng Python và thư viện Pygame, tích hợp chế độ chơi AI sử dụng thuật toán Negamax + Alpha-Beta Pruning cùng với 1 vài kĩ thuật tối ưu hóa khác để chơi thông minh với người chơi.

## 📖 Description
AI Connect Four là một trò chơi cổ điển nơi hai người chơi lần lượt thả quân cờ vào một bảng có 7 cột và 6 hàng. Người nào kết nối được 4 quân liên tiếp theo chiều ngang, dọc hoặc chéo trước sẽ chiến thắng.

Dự án này là bài tập lớn của bộ môn Trí tuệ nhân tạo. Trong dự án này, một đơn giản AI được xây dựng dựa trên thuật toán **Negamax** cùng với tối ưu **Alpha-beta pruning**, **Bitboard**, **TranpositionTable**, **Move Order** và **Iterative Deepening** để tăng tốc độ tính toán. Giao diện được xây dựng bằng Pygame, thân thiện và dễ sử dụng. Trò chơi hỗ trợ hiệu ứng di chuột, cảnh báo khi cột đầy, và AI phản hồi nhanh chóng với độ khó vừa phải. Trò chơi gồm 2 chế độ chơi VS Player (Chơi với người) và VS AI (Chơi với máy)

## ▶️ Getting Started

### Dependencies
- Python 3.12+
  + Nếu chưa có, có thể tải ở : [https://www.python.org/downloads/](https://www.python.org/downloads/)  
- Pygame
  + Cài đặt pip nếu chưa có :
    ```
    winget install --id=Python.Python.3.12 --source=winget
    ```
  + Cài đặt pygame :
    ```
    pip install pygame
    ```
- Windows 10 - 11

### Installing
Clone hoặc tải mã nguồn về từ GitHub:
```
git clone https://github.com/QuangCuong0711/AI_Connect_Four.git
cd AI-Connect-Four
```
Đảm bảo các file Coiny.ttf, background.jpg (nếu có), được đặt đúng trong thư mục assets/ hoặc cùng thư mục chạy.

### Executing Program
Chạy chương trình bằng lệnh sau trong terminal:
```
python main.py
```
**Bước chi tiết:**
  1. Cài python, pip, pygame nếu chưa có.
  2. Chạy main.py.
  3. Chọn chế độ chơi 
  4. Giao diện hiện ra: rê chuột để chọn cột, nhấn chuột để thả quân.
  5. Sử dụng các phím tắt
     - Nhấn R để chơi lại
     - Nhấn M để trở lại menu
     - Nhấn Q để thoát game

## 👥 Authors
- Đây là dự án cho bài tập lớn môn Trí tuệ nhân tạo tại Trường Đại học Công nghệ - ĐHQGHN
- Dự án có đóng góp của 4 sinh viên :
  + Đỗ Quang Cường - 23021484
  + Nguyễn Phương Linh - 23021609
  + Nguyễn Công Mạnh Hùng - 23021567
  + Trần Bình Dương - 23021514

## Demo


## Acknowledgments
- Các thuật toán trong bài được hướng dẫn và giảng dạy trong quá trình học môn **Trí tuệ nhân tạo**.
- Sản phẩm được phát triển dựa trên ý tưởng và kỹ thuật từ **Pascal Pons**, về cách xây dựng và tối ưu thuật toán cho trò chơi **Connect Four**.
