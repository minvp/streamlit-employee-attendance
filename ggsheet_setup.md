# 📊 Hướng dẫn kết nối Google Sheets để lưu dữ liệu lâu dài

## Tại sao dùng Google Sheets?

✅ **Ưu điểm:**
- Dữ liệu lưu trữ vĩnh viễn trên Google Cloud
- Không bị mất khi Streamlit Cloud restart
- Miễn phí 100%
- Có thể xem/sửa trực tiếp trên Google Sheets
- Nhiều người có thể truy cập cùng lúc
- Tự động sync và backup

❌ **So với Excel local:**
- Excel local: Mất dữ liệu khi deploy lên cloud
- Google Sheets: Dữ liệu an toàn mãi mãi

## Bước 1: Tạo Google Sheets

### 1.1. Tạo 2 Google Sheets mới

1. Vào https://sheets.google.com
2. Tạo sheet mới tên: **"Employee Attendance"**
3. Copy URL (ví dụ: `https://docs.google.com/spreadsheets/d/ABC123XYZ...`)
4. Copy **Spreadsheet ID** (phần ABC123XYZ giữa `/d/` và `/edit`)

5. Tạo thêm sheet thứ 2 tên: **"Employees"**
6. Copy Spreadsheet ID của sheet này

### 1.2. Cấu trúc Google Sheets

**Sheet "Employee Attendance":**
- Tab "2025-12", "2025-11", v.v. (sẽ tự động tạo)
- Cột: Tên NV | Ngày | Giờ vào | Giờ ra | Tổng giờ | Ghi chú

**Sheet "Employees":**
- Tab "Sheet1"
- Cột: Tên NV | Tiền công/ngày
- Thêm sẵn vài nhân viên mẫu:
  ```
  Nguyễn Văn A | 300000
  Trần Thị B | 250000
  Lê Văn C | 350000
  ```

## Bước 2: Cấu hình Google Cloud API

### 2.1. Tạo Google Cloud Project

1. Vào: https://console.cloud.google.com/
2. Đăng nhập bằng tài khoản Google
3. Nhấn **"Select a project"** → **"New Project"**
4. Tên project: `employee-attendance-app`
5. Nhấn **"Create"**

### 2.2. Bật Google Sheets API

1. Trong project vừa tạo, vào **"APIs & Services"** → **"Library"**
2. Tìm **"Google Sheets API"**
3. Nhấn **"Enable"**
4. Tìm **"Google Drive API"**
5. Nhấn **"Enable"**

### 2.3. Tạo Service Account

1. Vào **"APIs & Services"** → **"Credentials"**
2. Nhấn **"Create Credentials"** → **"Service Account"**
3. Điền thông tin:
   - **Service account name:** `attendance-app`
   - **Service account ID:** (tự động tạo)
   - **Description:** `Service account for employee attendance app`
4. Nhấn **"Create and Continue"**
5. **Role:** Chọn **"Editor"** (hoặc "Basic" → "Editor")
6. Nhấn **"Continue"** → **"Done"**

### 2.4. Tạo và tải Key JSON

1. Trong danh sách **Service Accounts**, nhấn vào account vừa tạo
2. Vào tab **"Keys"**
3. Nhấn **"Add Key"** → **"Create new key"**
4. Chọn **"JSON"**
5. Nhấn **"Create"**
6. File JSON sẽ được tải xuống (ví dụ: `employee-attendance-app-xxxxx.json`)
7. ⚠️ **GIỮ FILE NÀY AN TOÀN** - Không chia sẻ với ai!

### 2.5. Chia sẻ Google Sheets với Service Account

1. Mở file JSON vừa tải, tìm dòng `"client_email"`:
   ```json
   "client_email": "attendance-app@employee-attendance-app.iam.gserviceaccount.com"
   ```
2. Copy email này

3. Mở Google Sheet **"Employee Attendance"**
4. Nhấn **"Share"**
5. Paste email service account
6. Chọn quyền **"Editor"**
7. ❌ Bỏ chọn "Notify people"
8. Nhấn **"Share"**

9. Làm tương tự với Google Sheet **"Employees"**

## Bước 3: Cấu hình cho Local Development

### 3.1. Cài đặt thư viện

```powershell
pip install gspread google-auth
```

### 3.2. Tạo file .streamlit/secrets.toml

Tạo thư mục `.streamlit` trong `e:\Employee\`:

```powershell
mkdir .streamlit
```

Tạo file `secrets.toml` trong `.streamlit`:

```toml
# Google Sheets Configuration
[gcp_service_account]
type = "service_account"
project_id = "employee-attendance-app"
private_key_id = "xxxxx"
private_key = "-----BEGIN PRIVATE KEY-----\nxxxxx\n-----END PRIVATE KEY-----\n"
client_email = "attendance-app@employee-attendance-app.iam.gserviceaccount.com"
client_id = "xxxxx"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/xxxxx"

# Spreadsheet IDs
attendance_spreadsheet_id = "YOUR_ATTENDANCE_SHEET_ID_HERE"
employees_spreadsheet_id = "YOUR_EMPLOYEES_SHEET_ID_HERE"
```

**Lấy thông tin từ file JSON:**
- Mở file JSON đã tải ở bước 2.4
- Copy toàn bộ nội dung các trường vào `secrets.toml`
- Thay `YOUR_ATTENDANCE_SHEET_ID_HERE` bằng ID sheet chấm công
- Thay `YOUR_EMPLOYEES_SHEET_ID_HERE` bằng ID sheet nhân viên

⚠️ **Lưu ý về private_key:**
- Phải giữ nguyên format với `\n` cho xuống dòng
- Ví dụ: `"-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...\n-----END PRIVATE KEY-----\n"`

### 3.3. Cập nhật .gitignore

Đảm bảo file `.gitignore` có:

```
.streamlit/
*.json
secrets.toml
```

## Bước 4: Sử dụng app mới với Google Sheets

### 4.1. Chạy app mới

Tôi đã tạo file `app_gsheet.py` - version sử dụng Google Sheets.

```powershell
streamlit run app_gsheet.py
```

### 4.2. Kiểm tra kết nối

- App sẽ tự động kết nối Google Sheets
- Thử thêm nhân viên → Kiểm tra trên Google Sheets
- Thử chấm công → Kiểm tra sheet tháng được tạo

## Bước 5: Deploy lên Streamlit Cloud với Google Sheets

### 5.1. Push code lên GitHub

```powershell
git add .
git commit -m "Add Google Sheets integration"
git push
```

⚠️ **Đảm bảo:**
- File `.streamlit/secrets.toml` KHÔNG được push (có trong .gitignore)
- File JSON KHÔNG được push (có trong .gitignore)

### 5.2. Cấu hình Secrets trên Streamlit Cloud

1. Vào https://share.streamlit.io/
2. Chọn app của bạn
3. Nhấn **"Settings"** (⚙️) → **"Secrets"**
4. Copy toàn bộ nội dung file `.streamlit/secrets.toml`
5. Paste vào ô "Secrets"
6. Nhấn **"Save"**

### 5.3. Deploy

1. Trong settings app, chọn:
   - **Main file path:** `app_gsheet.py` (thay vì `app.py`)
2. Nhấn **"Save"**
3. App sẽ tự động redeploy

## Bước 6: Kiểm tra và sử dụng

### 6.1. Kiểm tra trên Streamlit Cloud

1. Mở app đã deploy
2. Thử chấm công
3. Mở Google Sheets → Kiểm tra dữ liệu đã lưu
4. ✅ Dữ liệu vẫn còn ngay cả khi app restart!

### 6.2. Sử dụng

**Ưu điểm của Google Sheets:**
- ✅ Dữ liệu an toàn vĩnh viễn
- ✅ Có thể xem trực tiếp trên Google Sheets
- ✅ Sửa trực tiếp trên Google Sheets (nếu cần)
- ✅ Chia sẻ với nhiều người
- ✅ Tự động backup bởi Google

**Sử dụng 2 phiên bản song song:**
- `app.py` - Version Excel local (cho máy tính cá nhân)
- `app_gsheet.py` - Version Google Sheets (cho cloud)

## 🔒 Bảo mật

**Quan trọng:**
- ❌ KHÔNG bao giờ commit file `.streamlit/secrets.toml` lên GitHub
- ❌ KHÔNG bao giờ commit file JSON lên GitHub
- ✅ Chỉ cấu hình secrets trên Streamlit Cloud
- ✅ Giữ file JSON ở máy cá nhân an toàn

## 🆘 Troubleshooting

### Lỗi: "gspread.exceptions.APIError"
- Kiểm tra đã bật Google Sheets API chưa
- Kiểm tra đã chia sẻ sheet với service account email chưa

### Lỗi: "Unable to find the server"
- Kiểm tra spreadsheet_id có đúng không
- Kiểm tra secrets.toml có đúng format không

### Lỗi: "private_key must be in PEM format"
- Kiểm tra private_key có giữ đúng format với `\n` không
- Copy lại từ file JSON, đảm bảo không bị mất ký tự

### Dữ liệu không hiện
- Refresh lại app
- Kiểm tra kết nối internet
- Xem logs trên Streamlit Cloud

## 📊 So sánh 2 phiên bản

| Tính năng | Excel Local | Google Sheets |
|-----------|-------------|---------------|
| Lưu trữ | File local | Google Cloud |
| Deploy cloud | ❌ Mất dữ liệu | ✅ An toàn |
| Chi phí | Miễn phí | Miễn phí |
| Truy cập web | ❌ | ✅ |
| Xem trực tiếp | Cần Excel | Google Sheets |
| Backup | Thủ công | Tự động |
| Đa người dùng | ❌ | ✅ |

## 🎉 Hoàn tất!

Bây giờ app của bạn:
- ✅ Lưu dữ liệu vĩnh viễn trên Google Sheets
- ✅ Không lo mất dữ liệu khi restart
- ✅ Có thể xem/sửa trên Google Sheets
- ✅ Sẵn sàng cho production!

## 📚 Tài liệu tham khảo

- Google Sheets API: https://developers.google.com/sheets/api
- gspread docs: https://docs.gspread.org/
- Streamlit secrets: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
