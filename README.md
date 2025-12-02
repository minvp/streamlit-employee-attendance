# 📋 Hệ thống chấm công nhân viên

Ứng dụng web chấm công đơn giản được xây dựng bằng Streamlit để quản lý thời gian làm việc của nhân viên.

## ✨ Tính năng

### 1. 📝 Chấm công
- Ghi nhận giờ vào/ra của nhân viên
- Tự động tính tổng giờ làm việc
- Thêm ghi chú cho từng lần chấm công
- Xem danh sách chấm công hôm nay

### 2. 👥 Quản lý nhân viên
- Thêm nhân viên mới với thông tin: Mã NV, Tên, Bộ phận, Chức vụ
- Xem danh sách tất cả nhân viên
- Xuất danh sách ra file Excel

### 3. 📊 Báo cáo
- Lọc dữ liệu theo tháng và nhân viên
- Xem báo cáo chi tiết từng lần chấm công
- Tổng hợp tổng giờ làm và số ngày công theo nhân viên
- Xuất báo cáo ra file Excel

### 4. 📈 Thống kê
- Biểu đồ tổng giờ làm việc theo nhân viên
- Biểu đồ số lượng chấm công theo ngày
- Các chỉ số thống kê: Tổng bản ghi, Số nhân viên, Tổng giờ làm, Trung bình giờ/ngày
- Top 5 nhân viên chăm chỉ nhất

## 🚀 Cài đặt

### Yêu cầu
- Python 3.7 trở lên
- pip

### Các bước cài đặt

1. Clone hoặc tải project về máy

2. Cài đặt các thư viện cần thiết:
```bash
pip install streamlit pandas openpyxl
```

## 💻 Chạy ứng dụng

Mở terminal/command prompt tại thư mục chứa file `app.py` và chạy lệnh:

```bash
streamlit run app.py
```

hoặc với virtual environment:

```bash
e:/Employee/.venv/Scripts/python.exe -m streamlit run app.py
```

Ứng dụng sẽ tự động mở trong trình duyệt web tại địa chỉ: `http://localhost:8501`

## 📁 Cấu trúc dữ liệu

Ứng dụng tự động tạo 2 file CSV để lưu trữ dữ liệu:

### 1. `employees.csv` - Danh sách nhân viên
- Mã NV
- Tên NV
- Bộ phận
- Chức vụ

### 2. `attendance_data.csv` - Dữ liệu chấm công
- Mã NV
- Tên NV
- Ngày
- Giờ vào
- Giờ ra
- Tổng giờ
- Ghi chú

## 📖 Hướng dẫn sử dụng

### Thêm nhân viên mới
1. Vào tab "👥 Quản lý nhân viên"
2. Điền thông tin: Mã NV, Tên, Bộ phận, Chức vụ
3. Nhấn nút "➕ Thêm nhân viên"

### Chấm công
1. Vào tab "📝 Chấm công"
2. Chọn nhân viên từ danh sách
3. Chọn ngày, giờ vào, giờ ra
4. Thêm ghi chú (nếu cần)
5. Nhấn nút "✅ Lưu chấm công"

### Xem báo cáo
1. Vào tab "📊 Báo cáo"
2. Lọc theo tháng hoặc nhân viên
3. Xem báo cáo chi tiết hoặc tổng hợp
4. Xuất ra Excel nếu cần

### Xem thống kê
1. Vào tab "📈 Thống kê"
2. Xem các biểu đồ và chỉ số thống kê
3. Xem top nhân viên chăm chỉ

## 🎨 Tính năng nổi bật

- ✅ Giao diện đơn giản, dễ sử dụng
- ✅ Tự động tính toán giờ làm việc
- ✅ Lưu trữ dữ liệu bằng CSV (dễ dàng sao lưu và chuyển đổi)
- ✅ Xuất báo cáo Excel
- ✅ Biểu đồ trực quan
- ✅ Không cần database phức tạp

## 🔧 Tùy chỉnh

Bạn có thể tùy chỉnh:
- Thay đổi giờ mặc định trong file `app.py`
- Thêm các trường thông tin khác
- Tùy chỉnh giao diện và màu sắc
- Thêm tính năng báo cáo mới

## 📝 Ghi chú

- Dữ liệu được lưu trữ trong các file CSV cùng thư mục với `app.py`
- Hệ thống tự động tạo 3 nhân viên mẫu khi chạy lần đầu
- File Excel xuất ra sẽ được lưu trong cùng thư mục

## 🤝 Đóng góp

Mọi đóng góp và góp ý đều được hoan nghênh!

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa theo nhu cầu.

---

**Phát triển bởi:** AI Assistant  
**Ngày tạo:** December 1, 2025
