import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import os
import csv
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Cấu hình trang
st.set_page_config(
    page_title="Hệ thống chấm công",
    page_icon="⏰",
    layout="wide"
)

# File lưu trữ dữ liệu
DATA_FILE = "attendance_data.xlsx"  # Đổi sang Excel
EMPLOYEE_FILE = "employees.csv"

# Khởi tạo file nếu chưa có
def init_files():
    if not os.path.exists(DATA_FILE):
        # Tạo file Excel trống
        df_empty = pd.DataFrame(columns=['Mã NV', 'Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])
        df_empty.to_excel(DATA_FILE, sheet_name='Template', index=False)
    
    if not os.path.exists(EMPLOYEE_FILE):
        with open(EMPLOYEE_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Mã NV', 'Tên NV', 'Bộ phận', 'Chức vụ'])
            # Thêm vài nhân viên mẫu
            writer.writerow(['NV001', 'Nguyễn Văn A', 'IT', 'Developer'])
            writer.writerow(['NV002', 'Trần Thị B', 'HR', 'Nhân viên'])
            writer.writerow(['NV003', 'Lê Văn C', 'Marketing', 'Manager'])

# Đọc danh sách nhân viên
def load_employees():
    if os.path.exists(EMPLOYEE_FILE):
        df = pd.read_csv(EMPLOYEE_FILE, encoding='utf-8')
        return df
    return pd.DataFrame(columns=['Mã NV', 'Tên NV', 'Bộ phận', 'Chức vụ'])

# Đọc dữ liệu chấm công (từ tất cả các sheet)
def load_attendance():
    if os.path.exists(DATA_FILE):
        try:
            # Đọc tất cả các sheet
            excel_file = pd.ExcelFile(DATA_FILE)
            all_sheets = []
            
            for sheet_name in excel_file.sheet_names:
                if sheet_name != 'Template':  # Bỏ qua sheet Template
                    df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)
                    if len(df) > 0:
                        all_sheets.append(df)
            
            if all_sheets:
                return pd.concat(all_sheets, ignore_index=True)
        except Exception as e:
            st.error(f"Lỗi đọc file Excel: {e}")
    
    return pd.DataFrame(columns=['Mã NV', 'Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])

# Đọc dữ liệu chấm công từ một sheet cụ thể
def load_attendance_by_month(month_year):
    """Đọc dữ liệu từ sheet theo tháng (format: YYYY-MM)"""
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, sheet_name=month_year)
            return df
        except Exception:
            # Sheet chưa tồn tại
            return pd.DataFrame(columns=['Mã NV', 'Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])
    return pd.DataFrame(columns=['Mã NV', 'Tên NV', 'Ngày', 'Giờ vào', 'Giờ ra', 'Tổng giờ', 'Ghi chú'])

# Lưu bản ghi chấm công vào sheet theo tháng
def save_attendance(employee_id, employee_name, date_str, time_in, time_out, total_hours, note):
    """Lưu dữ liệu chấm công vào sheet theo tháng"""
    # Xác định tên sheet theo tháng (format: YYYY-MM)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    sheet_name = date_obj.strftime("%Y-%m")  # Ví dụ: "2025-12"
    
    # Tạo bản ghi mới
    new_record = pd.DataFrame([{
        'Mã NV': employee_id,
        'Tên NV': employee_name,
        'Ngày': date_str,
        'Giờ vào': time_in,
        'Giờ ra': time_out,
        'Tổng giờ': total_hours,
        'Ghi chú': note
    }])
    
    try:
        # Đọc dữ liệu hiện tại từ sheet (nếu có)
        existing_df = load_attendance_by_month(sheet_name)
        
        # Gộp dữ liệu mới với dữ liệu cũ
        updated_df = pd.concat([existing_df, new_record], ignore_index=True)
        
        # Lưu lại vào Excel
        if os.path.exists(DATA_FILE):
            with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                updated_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Tạo file mới nếu chưa tồn tại
            with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
                updated_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
    except Exception as e:
        # Nếu file chưa tồn tại hoặc lỗi, tạo mới
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='w') as writer:
            new_record.to_excel(writer, sheet_name=sheet_name, index=False)

# Xóa bản ghi chấm công
def delete_attendance_record(sheet_name, index):
    """Xóa một bản ghi chấm công"""
    try:
        df = load_attendance_by_month(sheet_name)
        df = df.drop(index).reset_index(drop=True)
        
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        return True
    except Exception as e:
        st.error(f"Lỗi khi xóa: {e}")
        return False

# Cập nhật bản ghi chấm công
def update_attendance_record(sheet_name, index, employee_id, employee_name, date_str, time_in, time_out, total_hours, note):
    """Cập nhật một bản ghi chấm công"""
    try:
        df = load_attendance_by_month(sheet_name)
        df.loc[index] = [employee_id, employee_name, date_str, time_in, time_out, total_hours, note]
        
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        return True
    except Exception as e:
        st.error(f"Lỗi khi cập nhật: {e}")
        return False

# Thêm nhân viên mới
def add_employee(emp_id, emp_name, department, position):
    with open(EMPLOYEE_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([emp_id, emp_name, department, position])

# Tính tổng giờ làm việc (trừ 1 giờ ăn trưa)
def calculate_hours(time_in, time_out):
    if time_in and time_out:
        time_in_dt = datetime.strptime(time_in, "%H:%M")
        time_out_dt = datetime.strptime(time_out, "%H:%M")
        diff = time_out_dt - time_in_dt
        hours = diff.total_seconds() / 3600
        # Trừ 1 giờ ăn trưa
        hours = hours - 1.0
        # Đảm bảo không âm
        hours = max(0, hours)
        return round(hours, 2)
    return 0

# Khởi tạo
init_files()

# Header
st.title("⏰ Hệ thống chấm công nhân viên")
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
            # Tạo danh sách hiển thị
            employee_options = [f"{row['Mã NV']} - {row['Tên NV']}" for _, row in employees_df.iterrows()]
            selected_employee = st.selectbox("Chọn nhân viên", employee_options)
            
            # Lấy thông tin nhân viên
            emp_id = selected_employee.split(' - ')[0]
            emp_info = employees_df[employees_df['Mã NV'] == emp_id].iloc[0]
            
            st.info(f"**Bộ phận:** {emp_info['Bộ phận']} | **Chức vụ:** {emp_info['Chức vụ']}")
            
            attendance_date = st.date_input("Ngày", value=date.today())
            time_in = st.time_input("Giờ vào", value=time(8, 0))
            time_out = st.time_input("Giờ ra", value=time(17, 0))
            
            # Hiển thị tổng giờ tạm tính
            time_in_str = time_in.strftime("%H:%M")
            time_out_str = time_out.strftime("%H:%M")
            estimated_hours = calculate_hours(time_in_str, time_out_str)
            st.info(f"⏱️ **Tổng giờ làm việc:** {estimated_hours} giờ (đã trừ 1h ăn trưa)")
            
            note = st.text_area("Ghi chú (tùy chọn)")
            
            if st.button("✅ Lưu chấm công", type="primary", use_container_width=True):
                time_in_str = time_in.strftime("%H:%M")
                time_out_str = time_out.strftime("%H:%M")
                total_hours = calculate_hours(time_in_str, time_out_str)
                
                save_attendance(
                    emp_id,
                    emp_info['Tên NV'],
                    attendance_date.strftime("%Y-%m-%d"),
                    time_in_str,
                    time_out_str,
                    total_hours,
                    note
                )
                st.success(f"✅ Đã lưu chấm công cho {emp_info['Tên NV']} - Tổng: {total_hours} giờ")
                st.rerun()
        else:
            st.warning("⚠️ Chưa có nhân viên nào. Vui lòng thêm nhân viên ở tab 'Quản lý nhân viên'")
    
    with col2:
        st.subheader("Chấm công hôm nay")
        # Lấy dữ liệu từ sheet tháng hiện tại
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

# Tab 2: Sửa/Xóa dữ liệu
with tab2:
    st.header("✏️ Sửa hoặc Xóa dữ liệu chấm công")
    
    # Lấy danh sách các sheet (tháng)
    available_months = []
    if os.path.exists(DATA_FILE):
        try:
            excel_file = pd.ExcelFile(DATA_FILE)
            available_months = [sheet for sheet in excel_file.sheet_names if sheet != 'Template']
        except Exception:
            pass
    
    if available_months:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Chọn tháng")
            selected_month = st.selectbox("Tháng", sorted(available_months, reverse=True), key="edit_month")
        
        # Load dữ liệu tháng được chọn
        df_month = load_attendance_by_month(selected_month)
        
        if len(df_month) > 0:
            with col2:
                st.subheader(f"Dữ liệu tháng {selected_month}")
                st.info(f"Tổng: {len(df_month)} bản ghi")
            
            # Hiển thị bảng với index
            st.markdown("---")
            st.subheader("📋 Danh sách chấm công")
            
            # Tạo DataFrame với STT
            display_df = df_month.copy()
            display_df.insert(0, 'STT', range(1, len(display_df) + 1))
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Phần sửa/xóa
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
                    # Hiển thị thông tin bản ghi sẽ xóa
                    record_info = df_month.iloc[record_to_delete - 1]
                    st.info(f"""
                    **Bản ghi sẽ xóa:**
                    - Nhân viên: {record_info['Tên NV']}
                    - Ngày: {record_info['Ngày']}
                    - Giờ: {record_info['Giờ vào']} - {record_info['Giờ ra']}
                    """)
                    
                    if st.button("🗑️ Xác nhận xóa", type="secondary", use_container_width=True):
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
                    # Lấy thông tin bản ghi hiện tại
                    current_record = df_month.iloc[record_to_edit - 1]
                    
                    st.markdown("**Thông tin hiện tại:**")
                    
                    # Form sửa
                    employees_df = load_employees()
                    if len(employees_df) > 0:
                        # Tìm index của nhân viên hiện tại
                        emp_list = [f"{row['Mã NV']} - {row['Tên NV']}" for _, row in employees_df.iterrows()]
                        current_emp_str = f"{current_record['Mã NV']} - {current_record['Tên NV']}"
                        current_emp_idx = emp_list.index(current_emp_str) if current_emp_str in emp_list else 0
                        
                        new_employee = st.selectbox(
                            "Nhân viên", 
                            emp_list,
                            index=current_emp_idx,
                            key="edit_emp"
                        )
                        
                        new_emp_id = new_employee.split(' - ')[0]
                        new_emp_name = employees_df[employees_df['Mã NV'] == new_emp_id].iloc[0]['Tên NV']
                        
                        # Parse ngày hiện tại
                        current_date = datetime.strptime(str(current_record['Ngày']), "%Y-%m-%d").date()
                        new_date = st.date_input("Ngày", value=current_date, key="edit_date")
                        
                        # Parse giờ hiện tại
                        current_time_in = datetime.strptime(current_record['Giờ vào'], "%H:%M").time()
                        current_time_out = datetime.strptime(current_record['Giờ ra'], "%H:%M").time()
                        
                        new_time_in = st.time_input("Giờ vào", value=current_time_in, key="edit_time_in")
                        new_time_out = st.time_input("Giờ ra", value=current_time_out, key="edit_time_out")
                        
                        new_note = st.text_area("Ghi chú", value=str(current_record['Ghi chú']) if pd.notna(current_record['Ghi chú']) else "", key="edit_note")
                        
                        # Tính giờ mới
                        new_total_hours = calculate_hours(
                            new_time_in.strftime("%H:%M"),
                            new_time_out.strftime("%H:%M")
                        )
                        st.info(f"⏱️ Tổng giờ: {new_total_hours} giờ (đã trừ 1h ăn trưa)")
                        
                        if st.button("💾 Lưu thay đổi", type="primary", use_container_width=True):
                            if update_attendance_record(
                                selected_month,
                                record_to_edit - 1,
                                new_emp_id,
                                new_emp_name,
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
        new_emp_id = st.text_input("Mã nhân viên")
        new_emp_name = st.text_input("Tên nhân viên")
        new_department = st.text_input("Bộ phận")
        new_position = st.text_input("Chức vụ")
        
        if st.button("➕ Thêm nhân viên", type="primary", use_container_width=True):
            if new_emp_id and new_emp_name and new_department and new_position:
                employees_df = load_employees()
                if new_emp_id in employees_df['Mã NV'].values:
                    st.error("❌ Mã nhân viên đã tồn tại!")
                else:
                    add_employee(new_emp_id, new_emp_name, new_department, new_position)
                    st.success(f"✅ Đã thêm nhân viên {new_emp_name}")
                    st.rerun()
            else:
                st.warning("⚠️ Vui lòng điền đầy đủ thông tin")
    
    with col2:
        st.subheader("Danh sách nhân viên")
        employees_df = load_employees()
        if len(employees_df) > 0:
            st.dataframe(employees_df, use_container_width=True, hide_index=True)
            
            # Xuất file Excel
            if st.button("📥 Xuất danh sách (Excel)"):
                employees_df.to_excel("danh_sach_nhan_vien.xlsx", index=False)
                st.success("✅ Đã xuất file danh_sach_nhan_vien.xlsx")
        else:
            st.info("Chưa có nhân viên nào")

# Tab 4: Báo cáo
with tab4:
    st.header("Báo cáo chấm công")
    
    # Lấy danh sách các sheet (tháng) có sẵn
    available_months = []
    if os.path.exists(DATA_FILE):
        try:
            excel_file = pd.ExcelFile(DATA_FILE)
            available_months = [sheet for sheet in excel_file.sheet_names if sheet != 'Template']
        except Exception:
            pass
    
    if available_months:
        # Bộ lọc
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Lọc theo tháng (từ danh sách sheet)
            month_options = ["Tất cả"] + sorted(available_months, reverse=True)
            selected_month = st.selectbox("Chọn tháng", month_options)
        
        # Load dữ liệu theo lựa chọn
        if selected_month == "Tất cả":
            attendance_df = load_attendance()
        else:
            attendance_df = load_attendance_by_month(selected_month)
        
        with col2:
            # Lọc theo nhân viên
            if len(attendance_df) > 0:
                emp_options = ["Tất cả"] + sorted(attendance_df['Tên NV'].unique().tolist())
                selected_emp = st.selectbox("Chọn nhân viên", emp_options)
            else:
                selected_emp = "Tất cả"
                st.info("Không có dữ liệu")
        
        # Áp dụng bộ lọc
        if len(attendance_df) > 0:
            filtered_df = attendance_df.copy()
            
            # Đảm bảo cột Ngày là datetime
            filtered_df['Ngày'] = pd.to_datetime(filtered_df['Ngày'])
            
            # Lọc theo nhân viên
            if selected_emp != "Tất cả":
                filtered_df = filtered_df[filtered_df['Tên NV'] == selected_emp]
        else:
            filtered_df = attendance_df
        
        # Hiển thị dữ liệu
        if len(filtered_df) > 0:
            st.subheader(f"Tổng số bản ghi: {len(filtered_df)}")
            
            # Chuyển đổi lại định dạng ngày để hiển thị
            display_df = filtered_df.copy()
            display_df['Ngày'] = display_df['Ngày'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Bảng lương
            st.subheader("Bảng lương")
            salary_per_day = st.number_input(
                "Nhập số tiền công/ngày (VNĐ)",
                min_value=0,
                value=300000,
                step=10000,
                format="%d"
            )
            salary_summary = filtered_df.groupby('Tên NV').agg({'Ngày': 'count'}).reset_index()
            salary_summary.columns = ['Tên nhân viên', 'Số ngày công']
            salary_summary['Tiền công/ngày (VNĐ)'] = salary_per_day
            salary_summary['Tổng lương (VNĐ)'] = salary_summary['Số ngày công'] * salary_per_day
            st.dataframe(salary_summary, use_container_width=True, hide_index=True)

            # Xuất báo cáo
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Xuất báo cáo chi tiết (Excel)"):
                    filename = f"bao_cao_cham_cong_{selected_month if selected_month != 'Tất cả' else 'tat_ca'}.xlsx"
                    display_df.to_excel(filename, index=False)
                    st.success(f"✅ Đã xuất file {filename}")

            with col2:
                if st.button("📥 Xuất bảng lương (Excel)"):
                    filename = f"bang_luong_{selected_month if selected_month != 'Tất cả' else 'tat_ca'}.xlsx"
                    salary_summary.to_excel(filename, index=False)
                    st.success(f"✅ Đã xuất file {filename}")
        else:
            st.info("Không có dữ liệu phù hợp với bộ lọc")
    else:
        st.info("Chưa có dữ liệu chấm công")

# Tab 5: Thống kê
with tab5:
    st.header("Thống kê và biểu đồ")
    
    attendance_df = load_attendance()
    
    if len(attendance_df) > 0:
        attendance_df['Ngày'] = pd.to_datetime(attendance_df['Ngày'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Biểu đồ theo nhân viên
            st.subheader("Tổng giờ làm việc theo nhân viên")
            emp_hours = attendance_df.groupby('Tên NV')['Tổng giờ'].sum().sort_values(ascending=False)
            st.bar_chart(emp_hours)
        
        with col2:
            # Biểu đồ theo ngày
            st.subheader("Số lượng chấm công theo ngày")
            daily_count = attendance_df.groupby(attendance_df['Ngày'].dt.date).size()
            st.line_chart(daily_count)
        
        # Thống kê tổng quan
        st.subheader("Thống kê tổng quan")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_records = len(attendance_df)
            st.metric("Tổng số bản ghi", total_records)
        
        with col2:
            total_employees = attendance_df['Mã NV'].nunique()
            st.metric("Số nhân viên", total_employees)
        
        with col3:
            total_hours = attendance_df['Tổng giờ'].sum()
            st.metric("Tổng giờ làm", f"{total_hours:.2f} h")
        
        with col4:
            avg_hours = attendance_df['Tổng giờ'].mean()
            st.metric("Trung bình giờ/ngày", f"{avg_hours:.2f} h")
        
        # Top nhân viên chăm chỉ
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

# Tab 6: Xem dữ liệu
with tab6:
    st.header("📁 Quản lý dữ liệu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 File dữ liệu chấm công")
        st.info(f"**Tên file:** {DATA_FILE}")
        
        if os.path.exists(DATA_FILE):
            file_size = os.path.getsize(DATA_FILE) / 1024  # KB
            st.success(f"✅ File tồn tại - Kích thước: {file_size:.2f} KB")
            
            # Hiển thị danh sách các sheet
            try:
                excel_file = pd.ExcelFile(DATA_FILE)
                st.write(f"**Số sheet:** {len(excel_file.sheet_names)}")
                st.write("**Danh sách các tháng:**")
                for sheet in excel_file.sheet_names:
                    if sheet != 'Template':
                        df_sheet = pd.read_excel(DATA_FILE, sheet_name=sheet)
                        st.write(f"- 📅 **{sheet}** ({len(df_sheet)} bản ghi)")
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")
            
            # Nút tải xuống file Excel
            st.markdown("---")
            with open(DATA_FILE, 'rb') as f:
                st.download_button(
                    label="📥 Tải xuống file chấm công",
                    data=f,
                    file_name=DATA_FILE,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            # Xem nội dung file
            st.markdown("---")
            st.subheader("👁️ Xem nội dung từng sheet")
            try:
                excel_file = pd.ExcelFile(DATA_FILE)
                sheets_to_view = [s for s in excel_file.sheet_names if s != 'Template']
                if sheets_to_view:
                    selected_sheet = st.selectbox("Chọn sheet để xem", sheets_to_view)
                    df_view = pd.read_excel(DATA_FILE, sheet_name=selected_sheet)
                    st.dataframe(df_view, use_container_width=True, hide_index=True)
                    st.info(f"Tổng số bản ghi trong sheet **{selected_sheet}**: {len(df_view)}")
            except Exception as e:
                st.error(f"Lỗi: {e}")
        else:
            st.warning("⚠️ File chưa tồn tại. Hãy thêm dữ liệu chấm công để tạo file.")
    
    with col2:
        st.subheader("👥 File danh sách nhân viên")
        st.info(f"**Tên file:** {EMPLOYEE_FILE}")
        
        if os.path.exists(EMPLOYEE_FILE):
            file_size = os.path.getsize(EMPLOYEE_FILE) / 1024  # KB
            st.success(f"✅ File tồn tại - Kích thước: {file_size:.2f} KB")
            
            # Đếm số nhân viên
            emp_df = load_employees()
            st.write(f"**Tổng số nhân viên:** {len(emp_df)}")
            
            # Nút tải xuống file CSV
            st.markdown("---")
            with open(EMPLOYEE_FILE, 'rb') as f:
                st.download_button(
                    label="📥 Tải xuống danh sách nhân viên",
                    data=f,
                    file_name=EMPLOYEE_FILE,
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Xem nội dung file
            st.markdown("---")
            st.subheader("👁️ Xem nội dung file")
            st.dataframe(emp_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ File chưa tồn tại.")
    
    # Thông tin lưu trữ
    st.markdown("---")
    st.subheader("💾 Thông tin lưu trữ dữ liệu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📂 Vị trí lưu trữ:**
        - Dữ liệu được lưu trong thư mục hiện tại
        - File chấm công: `attendance_data.xlsx`
        - File nhân viên: `employees.csv`
        
        **🔒 Bảo vệ dữ liệu:**
        - Dữ liệu được lưu tự động khi nhập
        - Không bị mất khi tắt ứng dụng
        - Nên sao lưu định kỳ bằng nút tải xuống
        """)
    
    with col2:
        st.success("""
        **✅ Cấu trúc dữ liệu:**
        - Mỗi sheet Excel = 1 tháng
        - Format tên sheet: YYYY-MM
        - Ví dụ: `2025-12` = Tháng 12/2025
        
        **📊 Tính năng:**
        - Tự động tạo sheet theo tháng
        - Dễ dàng sao lưu và chia sẻ
        - Có thể mở bằng Excel/LibreOffice
        """)

# Footer
st.markdown("---")
st.markdown("🏢 **Hệ thống chấm công nhân viên** | © 2025")
st.caption("💡 **Lưu ý:** Tổng giờ làm việc đã tự động trừ 1 giờ ăn trưa")
