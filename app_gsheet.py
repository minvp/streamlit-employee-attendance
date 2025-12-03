import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import gspread
from google.oauth2.service_account import Credentials

# Cấu hình trang
st.set_page_config(
    page_title="Hệ thống chấm công",
    page_icon="⏰",
    layout="wide"
)

# Cấu hình Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Kết nối Google Sheets
@st.cache_resource
def get_gspread_client():
    """Khởi tạo kết nối Google Sheets"""
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Lỗi kết nối Google Sheets: {e}")
        st.info("Vui lòng kiểm tra cấu hình secrets trong .streamlit/secrets.toml")
        return None

# Hàm lấy Sheet IDs
@st.cache_data
def get_sheet_ids():
    """Lấy Spreadsheet IDs từ secrets"""
    try:
        return {
            'attendance': st.secrets["attendance_spreadsheet_id"],
            'employees': st.secrets["employees_spreadsheet_id"]
        }
    except Exception as e:
        st.error("⚠️ Chưa cấu hình spreadsheet IDs trong secrets.toml")
        st.error(f"Chi tiết lỗi: {e}")
        st.stop()
        return None

# Đọc danh sách nhân viên từ Google Sheets
@st.cache_data(ttl=60)
def load_employees():
    """Đọc danh sách nhân viên từ Google Sheets"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        sheet = gc.open_by_key(sheet_ids['employees']).sheet1
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data)
        else:
            # Tạo dữ liệu mẫu nếu sheet trống
            df_empty = pd.DataFrame(columns=['Tên NV', 'Tiền công/ngày'])
            return df_empty
    except Exception as e:
        st.error(f"Lỗi đọc danh sách nhân viên: {e}")
        return pd.DataFrame(columns=['Tên NV', 'Tiền công/ngày'])

# Đọc dữ liệu chấm công từ một sheet cụ thể
@st.cache_data(ttl=30)
def load_attendance_by_month(month_year):
    """Đọc dữ liệu từ sheet theo tháng (format: YYYY-MM)"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        spreadsheet = gc.open_by_key(sheet_ids['attendance'])
        
        # Kiểm tra sheet có tồn tại không
        try:
            worksheet = spreadsheet.worksheet(month_year)
            data = worksheet.get_all_records()
            if data:
                return pd.DataFrame(data)
        except gspread.exceptions.WorksheetNotFound:
            pass
        
        return pd.DataFrame(columns=['Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu chấm công: {e}")
        return pd.DataFrame(columns=['Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])

# Đọc tất cả dữ liệu chấm công
@st.cache_data(ttl=60)
def load_attendance():
    """Đọc dữ liệu từ tất cả các sheet"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        spreadsheet = gc.open_by_key(sheet_ids['attendance'])
        worksheets = spreadsheet.worksheets()
        
        all_data = []
        for ws in worksheets:
            # Bỏ qua sheet Template hoặc sheet mặc định
            if ws.title not in ['Sheet1', 'Template']:
                data = ws.get_all_records()
                if data:
                    all_data.extend(data)
        
        if all_data:
            return pd.DataFrame(all_data)
        return pd.DataFrame(columns=['Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])
    except Exception as e:
        st.error(f"Lỗi đọc tất cả dữ liệu: {e}")
        return pd.DataFrame(columns=['Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])

# Lưu bản ghi chấm công
def save_attendance(employee_name, date_str, time_in, time_out, total_hours, note):
    """Lưu dữ liệu chấm công vào Google Sheets"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        # Xác định tên sheet theo tháng
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        sheet_name = date_obj.strftime("%Y-%m")
        
        spreadsheet = gc.open_by_key(sheet_ids['attendance'])
        
        # Tạo hoặc lấy worksheet
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Tạo sheet mới
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="6")
            # Thêm header
            worksheet.append_row(['Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])
        
        # Thêm dữ liệu
        worksheet.append_row([employee_name, date_str, time_in, time_out, total_hours, note])
        
        # Clear cache để refresh dữ liệu
        load_attendance_by_month.clear()
        load_attendance.clear()
        
        return True
    except Exception as e:
        st.error(f"Lỗi lưu dữ liệu: {e}")
        return False

# Xóa bản ghi chấm công
def delete_attendance_record(sheet_name, row_index):
    """Xóa một bản ghi chấm công (row_index là STT hiển thị, bắt đầu từ 1)"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        spreadsheet = gc.open_by_key(sheet_ids['attendance'])
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # row_index + 1 vì row 1 là header, +1 nữa vì index bắt đầu từ 1
        actual_row = row_index + 2
        worksheet.delete_rows(actual_row)
        
        # Clear cache
        load_attendance_by_month.clear()
        load_attendance.clear()
        
        return True
    except Exception as e:
        st.error(f"Lỗi xóa dữ liệu: {e}")
        return False

# Cập nhật bản ghi chấm công
def update_attendance_record(sheet_name, row_index, employee_name, date_str, time_in, time_out, total_hours, note):
    """Cập nhật một bản ghi chấm công"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        spreadsheet = gc.open_by_key(sheet_ids['attendance'])
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # row_index + 2 vì row 1 là header
        actual_row = row_index + 2
        worksheet.update(f'A{actual_row}:F{actual_row}', 
                        [[employee_name, date_str, time_in, time_out, total_hours, note]])
        
        # Clear cache
        load_attendance_by_month.clear()
        load_attendance.clear()
        
        return True
    except Exception as e:
        st.error(f"Lỗi cập nhật dữ liệu: {e}")
        return False

# Thêm nhân viên mới
def add_employee(emp_name, daily_wage):
    """Thêm nhân viên mới vào Google Sheets"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        sheet = gc.open_by_key(sheet_ids['employees']).sheet1
        
        # Kiểm tra nếu sheet trống, thêm header
        if sheet.row_count == 0 or len(sheet.get_all_values()) == 0:
            sheet.append_row(['Tên NV', 'Tiền công/ngày'])
        
        sheet.append_row([emp_name, daily_wage])
        
        # Clear cache
        load_employees.clear()
        
        return True
    except Exception as e:
        st.error(f"Lỗi thêm nhân viên: {e}")
        return False

# Tính tổng giờ làm việc (trừ 1 giờ ăn trưa)
def calculate_hours(time_in, time_out):
    if time_in and time_out:
        time_in_dt = datetime.strptime(time_in, "%H:%M")
        time_out_dt = datetime.strptime(time_out, "%H:%M")
        diff = time_out_dt - time_in_dt
        hours = diff.total_seconds() / 3600
        hours = hours - 1.0
        hours = max(0, hours)
        return round(hours, 2)
    return 0

# Lấy danh sách các sheet (tháng)
@st.cache_data(ttl=60)
def get_available_months():
    """Lấy danh sách các tháng có sẵn"""
    try:
        gc = get_gspread_client()
        sheet_ids = get_sheet_ids()
        spreadsheet = gc.open_by_key(sheet_ids['attendance'])
        worksheets = spreadsheet.worksheets()
        months = [ws.title for ws in worksheets if ws.title not in ['Sheet1', 'Template']]
        return months
    except Exception as e:
        st.error(f"Lỗi lấy danh sách tháng: {e}")
        return []

# Header
st.title("⏰ Hệ thống chấm công nhân viên")
st.success("✅ Đã kết nối Google Sheets - Dữ liệu được lưu trữ vĩnh viễn")
st.markdown("---")

# Tạo tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📝 Chấm công", "✏️ Sửa/Xóa", "👥 Quản lý nhân viên", "📊 Báo cáo", "📈 Thống kê", "📁 Dữ liệu"])

# Tab 1: Chấm công
with tab1:
    st.header("Chấm công hàng ngày")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Thông tin chấm công")
        
        employees_df = load_employees()
        if len(employees_df) > 0:
            employee_options = [row['Tên NV'] for _, row in employees_df.iterrows()]
            selected_employee = st.selectbox("Chọn nhân viên", employee_options)
            
            # Lấy thông tin tiền công
            emp_info = employees_df[employees_df['Tên NV'] == selected_employee].iloc[0]
            st.info(f"💰 **Tiền công/ngày:** {emp_info['Tiền công/ngày']:,} VNĐ")
            
            attendance_date = st.date_input("Ngày", value=date.today())
            time_in = st.time_input("Giờ vào", value=time(8, 0))
            time_out = st.time_input("Giờ ra", value=time(17, 0))
            
            time_in_str = time_in.strftime("%H:%M")
            time_out_str = time_out.strftime("%H:%M")
            estimated_hours = calculate_hours(time_in_str, time_out_str)
            st.info(f"⏱️ **Tổng giờ làm việc:** {estimated_hours} giờ (đã trừ 1h ăn trưa)")
            
            note = st.text_area("Ghi chú (tùy chọn)")
            
            if st.button("✅ Lưu chấm công", type="primary", use_container_width=True):
                with st.spinner("Đang lưu vào Google Sheets..."):
                    if save_attendance(
                        selected_employee,
                        attendance_date.strftime("%Y-%m-%d"),
                        time_in_str,
                        time_out_str,
                        estimated_hours,
                        note
                    ):
                        st.success(f"✅ Đã lưu chấm công cho {selected_employee} - Tổng: {estimated_hours} giờ")
                        st.rerun()
                    else:
                        st.error("❌ Có lỗi khi lưu dữ liệu")
        else:
            st.warning("⚠️ Chưa có nhân viên nào. Vui lòng thêm nhân viên ở tab 'Quản lý nhân viên'")
    
    with col2:
        st.subheader("Chấm công hôm nay")
        current_month = date.today().strftime("%Y-%m")
        today_str = date.today().strftime("%Y-%m-%d")
        
        month_attendance = load_attendance_by_month(current_month)
        if len(month_attendance) > 0:
            today_attendance = month_attendance[month_attendance['Ngày'] == today_str]
            if len(today_attendance) > 0:
                st.dataframe(today_attendance, use_container_width=True, hide_index=True)
            else:
                st.info("Chưa có bản ghi chấm công nào hôm nay")
        else:
            st.info("Chưa có dữ liệu chấm công trong tháng này")

# Tab 2: Sửa/Xóa
with tab2:
    st.header("✏️ Sửa hoặc Xóa dữ liệu chấm công")
    
    available_months = get_available_months()
    
    if available_months:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Chọn tháng")
            selected_month = st.selectbox("Tháng", sorted(available_months, reverse=True), key="edit_month")
        
        df_month = load_attendance_by_month(selected_month)
        
        if len(df_month) > 0:
            with col2:
                st.subheader(f"Dữ liệu tháng {selected_month}")
                st.info(f"Tổng: {len(df_month)} bản ghi")
            
            st.markdown("---")
            st.subheader("📋 Danh sách chấm công")
            
            display_df = df_month.copy()
            display_df.insert(0, 'STT', range(1, len(display_df) + 1))
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🗑️ Xóa bản ghi")
                st.warning("⚠️ Lưu ý: Hành động này không thể hoàn tác!")
                
                record_to_delete = st.number_input(
                    "Nhập STT cần xóa", 
                    min_value=1, 
                    max_value=len(df_month),
                    value=1,
                    key="delete_stt"
                )
                
                if record_to_delete:
                    record_info = df_month.iloc[record_to_delete - 1]
                    st.info(f"""
                    **Bản ghi sẽ xóa:**
                    - Nhân viên: {record_info['Tên NV']}
                    - Ngày: {record_info['Ngày']}
                    - Giờ: {record_info['Giờ vào']} - {record_info['Giờ ra']}
                    """)
                    
                    if st.button("🗑️ Xác nhận xóa", type="secondary", use_container_width=True):
                        with st.spinner("Đang xóa..."):
                            if delete_attendance_record(selected_month, record_to_delete - 1):
                                st.success("✅ Đã xóa bản ghi!")
                                st.rerun()
            
            with col2:
                st.subheader("✏️ Sửa bản ghi")
                
                record_to_edit = st.number_input(
                    "Nhập STT cần sửa", 
                    min_value=1, 
                    max_value=len(df_month),
                    value=1,
                    key="edit_stt"
                )
                
                if record_to_edit:
                    current_record = df_month.iloc[record_to_edit - 1]
                    st.markdown("**Thông tin hiện tại:**")
                    
                    employees_df = load_employees()
                    if len(employees_df) > 0:
                        emp_list = [row['Tên NV'] for _, row in employees_df.iterrows()]
                        current_emp_idx = emp_list.index(current_record['Tên NV']) if current_record['Tên NV'] in emp_list else 0
                        
                        new_employee = st.selectbox(
                            "Nhân viên", 
                            emp_list,
                            index=current_emp_idx,
                            key="edit_emp"
                        )
                        
                        current_date = datetime.strptime(str(current_record['Ngày']), "%Y-%m-%d").date()
                        new_date = st.date_input("Ngày", value=current_date, key="edit_date")
                        
                        current_time_in = datetime.strptime(current_record['Giờ vào'], "%H:%M").time()
                        current_time_out = datetime.strptime(current_record['Giờ ra'], "%H:%M").time()
                        
                        new_time_in = st.time_input("Giờ vào", value=current_time_in, key="edit_time_in")
                        new_time_out = st.time_input("Giờ ra", value=current_time_out, key="edit_time_out")
                        
                        new_note = st.text_area("Ghi chú", value=str(current_record['Ghi chú']) if pd.notna(current_record['Ghi chú']) else "", key="edit_note")
                        
                        new_total_hours = calculate_hours(
                            new_time_in.strftime("%H:%M"),
                            new_time_out.strftime("%H:%M")
                        )
                        st.info(f"⏱️ Tổng giờ: {new_total_hours} giờ (đã trừ 1h ăn trưa)")
                        
                        if st.button("💾 Lưu thay đổi", type="primary", use_container_width=True):
                            with st.spinner("Đang cập nhật..."):
                                if update_attendance_record(
                                    selected_month,
                                    record_to_edit - 1,
                                    new_employee,
                                    new_date.strftime("%Y-%m-%d"),
                                    new_time_in.strftime("%H:%M"),
                                    new_time_out.strftime("%H:%M"),
                                    new_total_hours,
                                    new_note
                                ):
                                    st.success("✅ Đã cập nhật bản ghi!")
                                    st.rerun()
        else:
            st.info(f"Tháng {selected_month} chưa có dữ liệu")
    else:
        st.warning("⚠️ Chưa có dữ liệu chấm công. Hãy thêm dữ liệu ở tab 'Chấm công' trước.")

# Tab 3: Quản lý nhân viên
with tab3:
    st.header("Quản lý nhân viên")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Thêm nhân viên mới")
        new_emp_name = st.text_input("Tên nhân viên")
        new_daily_wage = st.number_input("Tiền công/ngày (VNĐ)", min_value=0, value=300000, step=10000)
        
        if st.button("➕ Thêm nhân viên", type="primary", use_container_width=True):
            if new_emp_name:
                employees_df = load_employees()
                if new_emp_name in employees_df['Tên NV'].values:
                    st.error("❌ Tên nhân viên đã tồn tại!")
                else:
                    with st.spinner("Đang thêm nhân viên..."):
                        if add_employee(new_emp_name, new_daily_wage):
                            st.success(f"✅ Đã thêm nhân viên {new_emp_name} - {new_daily_wage:,} VNĐ/ngày")
                            st.rerun()
            else:
                st.warning("⚠️ Vui lòng nhập tên nhân viên")
    
    with col2:
        st.subheader("Danh sách nhân viên")
        employees_df = load_employees()
        if len(employees_df) > 0:
            st.dataframe(employees_df, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có nhân viên nào")

# Tab 4: Báo cáo (tương tự app.py nhưng dùng Google Sheets)
with tab4:
    st.header("Báo cáo chấm công")
    
    available_months = get_available_months()
    
    if available_months:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            month_options = ["Tất cả"] + sorted(available_months, reverse=True)
            selected_month = st.selectbox("Chọn tháng", month_options)
        
        if selected_month == "Tất cả":
            attendance_df = load_attendance()
        else:
            attendance_df = load_attendance_by_month(selected_month)
        
        with col2:
            if len(attendance_df) > 0:
                emp_options = ["Tất cả"] + sorted(attendance_df['Tên NV'].unique().tolist())
                selected_emp = st.selectbox("Chọn nhân viên", emp_options)
            else:
                selected_emp = "Tất cả"
                st.info("Không có dữ liệu")
        
        if len(attendance_df) > 0:
            filtered_df = attendance_df.copy()
            filtered_df['Ngày'] = pd.to_datetime(filtered_df['Ngày'])
            
            if selected_emp != "Tất cả":
                filtered_df = filtered_df[filtered_df['Tên NV'] == selected_emp]
        else:
            filtered_df = attendance_df
        
        if len(filtered_df) > 0:
            st.subheader(f"Tổng số bản ghi: {len(filtered_df)}")
            
            display_df = filtered_df.copy()
            display_df['Ngày'] = display_df['Ngày'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.subheader("Tổng hợp giờ làm theo nhân viên")
            summary = filtered_df.groupby('Tên NV')['Tổng giờ'].agg(['sum', 'count']).reset_index()
            summary.columns = ['Tên nhân viên', 'Tổng giờ làm', 'Số ngày công']
            summary['Tổng giờ làm'] = summary['Tổng giờ làm'].round(2)
            st.dataframe(summary, use_container_width=True, hide_index=True)
        else:
            st.info("Không có dữ liệu phù hợp với bộ lọc")
    else:
        st.info("Chưa có dữ liệu chấm công")

# Tab 5: Thống kê (tương tự app.py)
with tab5:
    st.header("Thống kê và biểu đồ")
    
    attendance_df = load_attendance()
    
    if len(attendance_df) > 0:
        attendance_df['Ngày'] = pd.to_datetime(attendance_df['Ngày'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Tổng giờ làm việc theo nhân viên")
            emp_hours = attendance_df.groupby('Tên NV')['Tổng giờ'].sum().sort_values(ascending=False)
            st.bar_chart(emp_hours)
        
        with col2:
            st.subheader("Số lượng chấm công theo ngày")
            daily_count = attendance_df.groupby(attendance_df['Ngày'].dt.date).size()
            st.line_chart(daily_count)
        
        st.subheader("Thống kê tổng quan")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tổng số bản ghi", len(attendance_df))
        with col2:
            st.metric("Số nhân viên", attendance_df['Tên NV'].nunique())
        with col3:
            st.metric("Tổng giờ làm", f"{attendance_df['Tổng giờ'].sum():.2f} h")
        with col4:
            st.metric("Trung bình giờ/ngày", f"{attendance_df['Tổng giờ'].mean():.2f} h")
        
        st.subheader("🏆 Top 5 nhân viên chăm chỉ nhất")
        top_employees = attendance_df.groupby('Tên NV').agg({
            'Tổng giờ': 'sum',
            'Ngày': 'count'
        }).round(2)
        top_employees.columns = ['Tổng giờ làm', 'Số ngày công']
        top_employees = top_employees.sort_values('Tổng giờ làm', ascending=False).head(5)
        st.dataframe(top_employees, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu để thống kê")

# Tab 6: Thông tin Google Sheets
with tab6:
    st.header("📁 Quản lý dữ liệu Google Sheets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Dữ liệu chấm công")
        st.info("Dữ liệu được lưu trữ trên Google Sheets")
        
        try:
            gc = get_gspread_client()
            sheet_ids = get_sheet_ids()
            spreadsheet = gc.open_by_key(sheet_ids['attendance'])
            st.success(f"✅ Kết nối thành công: **{spreadsheet.title}**")
            
            worksheets = spreadsheet.worksheets()
            # st.write(f"**Số sheet:** {len(worksheets)}")
            # st.write("**Danh sách các tháng:**")
            # for ws in worksheets:
            #     if ws.title not in ['Sheet1', 'Template']:
            #         st.write(f"- 📅 **{ws.title}** ({ws.row_count - 1} bản ghi)")
            
            st.markdown("---")
            st.markdown(f"🔗 [Mở Google Sheets](https://docs.google.com/spreadsheets/d/{sheet_ids['attendance']})")
        except Exception as e:
            st.error(f"Lỗi: {e}")
    
    with col2:
        st.subheader("👥 Danh sách nhân viên")
        st.info("Dữ liệu được lưu trữ trên Google Sheets")
        
        try:
            gc = get_gspread_client()
            sheet_ids = get_sheet_ids()
            spreadsheet = gc.open_by_key(sheet_ids['employees'])
            st.success(f"✅ Kết nối thành công: **{spreadsheet.title}**")
            
            emp_df = load_employees()
            # st.write(f"**Tổng số nhân viên:** {len(emp_df)}")
            
            st.markdown("---")
            st.markdown(f"🔗 [Mở Google Sheets](https://docs.google.com/spreadsheets/d/{sheet_ids['employees']})")
        except Exception as e:
            st.error(f"Lỗi: {e}")
    
    st.markdown("---")
    st.subheader("💾 Ưu điểm của Google Sheets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **✅ Lưu trữ an toàn:**
        - Dữ liệu trên Google Cloud
        - Không bị mất khi app restart
        - Tự động backup bởi Google
        - Truy cập từ bất kỳ đâu
        """)
    
    with col2:
        st.info("""
        **📊 Dễ dàng quản lý:**
        - Xem trực tiếp trên Google Sheets
        - Sửa trực tiếp nếu cần
        - Chia sẻ với nhiều người
        - Export sang Excel, CSV, PDF
        """)

# Footer
st.markdown("---")
st.markdown("🏢 **Hệ thống chấm công nhân viên** | © 2025")
st.caption("💡 **Lưu ý:** Tổng giờ làm việc đã tự động trừ 1 giờ ăn trưa")
st.caption("☁️ **Lưu trữ:** Dữ liệu được lưu an toàn trên Google Sheets")
