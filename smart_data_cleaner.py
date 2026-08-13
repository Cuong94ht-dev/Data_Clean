import streamlit as st

# 1. Cấu hình danh sách Tài khoản & Mật khẩu cho team
USERS = {
    "admin": "123abc",
}

def check_password():
    """Hàm kiểm tra mật khẩu"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    # Giao diện màn hình đăng nhập
    st.title("🔒 Đăng nhập Hệ thống Nội bộ")
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập", type="primary"):
        if username in USERS and USERS[username] == password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Mật khẩu hoặc tài khoản không đúng!")
            
    return False

# ---------------------------------------------------------
# QUẢN LÝ LUỒNG CHẠY CỦA APP
# ---------------------------------------------------------
if check_password():
    # --- NỘI DUNG CHÍNH CỦA APP (Chỉ hiển thị khi đã đăng nhập thành công) ---
    st.sidebar.success(f"Xin chào!")
    if st.sidebar.button("Đăng xuất"):
        st.session_state["authenticated"] = False
        st.rerun()


    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    # Cấu hình trang giao diện rộng rãi
    st.set_page_config(
        page_title="Smart Data Cleaner",
        page_icon="🧹",
        layout="wide"
    )

    # Tiêu đề chính
    st.title("🧹 Smart Data Cleaner Web App")
    st.markdown("""
    Ứng dụng giúp bạn **phát hiện, phân tích và xử lý dữ liệu khuyết thiếu (NaN)** một cách trực quan và nhanh chóng.
    Chỉ cần tải tệp CSV của bạn lên, hệ thống sẽ tự động quét, vẽ biểu đồ báo cáo và cung cấp các công cụ làm sạch dữ liệu thực chiến!

    """)

    st.markdown("---")

    # 1. Cổng tải tệp tin (Sử dụng tham số type=['csv'] chuẩn xác)
    uploaded_file = st.file_uploader("Tải lên tệp dữ liệu CSV của bạn:",type="csv")

    if uploaded_file is not None:
        # Đọc dữ liệu từ file tải lên
        try:
            df = pd.read_csv(uploaded_file)
            
            # Tạo bản sao để thực hiện các thao tác làm sạch dữ liệu
            df_cleaned = df.copy()
            
            # Chia bố cục giao diện làm 2 cột chính
            col_left, col_right = st.columns([1, 1], gap="large")
            
            with col_left:
                st.subheader("📊 Xem trước dữ liệu gốc (5 dòng đầu)")
                st.dataframe(df.head(5), use_container_width=True)
                
                # Thông tin tổng quan của dữ liệu
                st.markdown("**Thông tin tổng quan:**")
                st.write(f"- 📈 Kích thước: `{df.shape[0]}` dòng và `{df.shape[1]}` cột.")
                
                # Tính toán thống kê dữ liệu khuyết thiếu (NaN)
                nan_counts = df.isna().sum()
                total_nan = nan_counts.sum()
                
                # Hiển thị Metric tổng số ô bị khuyết thiếu
                st.metric(label="Tổng số ô bị khuyết thiếu (NaN)", value=total_nan, 
                        delta="Cần xử lý!" if total_nan > 0 else "Dữ liệu hoàn hảo!", )
                
            with col_right:
                st.subheader("📈 Biểu đồ thống kê dữ liệu khuyết thiếu")
                
                if total_nan > 0:
                    # Chỉ lấy các cột có NaN để vẽ biểu đồ cho trực quan
                    nan_only = nan_counts[nan_counts > 0]
                    
                    # Vẽ biểu đồ cột Matplotlib
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.bar(nan_only.index, nan_only.values, color='#ff4b4b', edgecolor='black', alpha=0.8)
                    
                    # Trang trí biểu đồ
                    ax.set_title("Số lượng giá trị khuyết thiếu theo từng cột", fontsize=11, fontweight='bold')
                    ax.set_ylabel("Số lượng ô trống (NaN)", fontsize=9)
                    ax.set_xlabel("Tên cột dữ liệu", fontsize=9)
                    plt.xticks(rotation=45, ha='right', fontsize=8)
                    plt.yticks(fontsize=8)
                    ax.grid(axis='y', linestyle='--', alpha=0.5)
                    
                    # Hiển thị số liệu cụ thể trên đầu mỗi cột
                    for i, v in enumerate(nan_only.values):
                        ax.text(i, v + (max(nan_only.values)*0.02), str(v), ha='center', va='bottom', fontsize=8, fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.success("🎉 Tuyệt vời! Bộ dữ liệu của bạn không chứa bất kỳ giá trị khuyết thiếu (NaN) nào!")
            
            st.markdown("---")
            
            # PHẦN 2: CÔNG CỤ LÀM SẠCH DỮ LIỆU
            st.subheader("⚙️ Hộp công cụ làm sạch dữ liệu")
            
            if total_nan > 0:
                # Tạo 3 cột để phân chia các tùy chọn làm sạch
                col_tool1, col_tool2 = st.columns([1, 2], gap="medium")
                
                with col_tool1:
                    # 1. Lựa chọn chiến lược xử lý NaN
                    option = st.selectbox(
                        "Lựa chọn chiến lược xử lý NaN:",
                        [
                            "Giữ nguyên dữ liệu",
                            "Xóa bỏ (dropna) - Xóa hàng chứa bất kỳ ô trống nào",
                            "Xóa bỏ (dropna) - Chỉ xóa hàng nếu cột chỉ định bị trống",
                            "Điền khuyết (fillna) - Điền toàn bộ bằng số 0",
                            "Điền khuyết (fillna) - Điền bằng Giá trị trung bình (Mean)",
                            "Điền khuyết (fillna) - Lan truyền dữ liệu tiến (Forward Fill)",
                            "Điền khuyết (fillna) - Lan truyền dữ liệu lùi (Backward Fill)"
                        ]
                    )
                
                with col_tool2:
                    # 2. Thực thi xử lý dựa trên lựa chọn của người dùng
                    if option == "Giữ nguyên dữ liệu":
                        df_cleaned = df.copy()
                        st.info("💡 Bạn đang ở chế độ xem dữ liệu gốc. Hãy chọn một chiến lược làm sạch ở bên cạnh.")
                        
                    elif option == "Xóa bỏ (dropna) - Xóa hàng chứa bất kỳ ô trống nào":
                        df_cleaned = df.dropna()
                        st.warning(f"⚠️ Đã loại bỏ `{df.shape[0] - df_cleaned.shape[0]}` hàng chứa giá trị khuyết thiếu.")
                        
                    elif option == "Xóa bỏ (dropna) - Chỉ xóa hàng nếu cột chỉ định bị trống":
                        selected_col = st.selectbox("Chọn cột làm mốc để kiểm tra NaN:", df.columns)
                        df_cleaned = df.dropna(subset=[selected_col])
                        st.warning(f"⚠️ Đã loại bỏ `{df.shape[0] - df_cleaned.shape[0]}` hàng có cột `{selected_col}` bị trống.")
                        
                    elif option == "Điền khuyết (fillna) - Điền toàn bộ bằng số 0":
                        df_cleaned = df.fillna(0)
                        st.success("✅ Đã điền toàn bộ giá trị khuyết thiếu (NaN) bằng số 0.")
                        
                    elif option == "Điền khuyết (fillna) - Điền bằng Giá trị trung bình (Mean)":
                        # Chỉ điền Mean cho các cột dữ liệu số
                        num_cols = df.select_dtypes(include=[np.number]).columns
                        for col in num_cols:
                            df_cleaned[col] = df[col].fillna(df[col].mean())
                        st.success(f"✅ Đã điền giá trị khuyết thiếu bằng số Trung bình (Mean) trên các cột số: {list(num_cols)}")
                        
                    elif option == "Điền khuyết (fillna) - Lan truyền dữ liệu tiến (Forward Fill)":
                        df_cleaned = df.ffill()
                        st.success("✅ Đã xử lý bằng phương pháp Lan truyền tiến (Forward Fill - ffill).")
                        
                    elif option == "Điền khuyết (fillna) - Lan truyền dữ liệu lùi (Backward Fill)":
                        df_cleaned = df.bfill()
                        st.success("✅ Đã xử lý bằng phương pháp Lan truyền lùi (Backward Fill - bfill).")
                
                st.markdown("### 🔍 So sánh Dữ liệu trước và sau khi làm sạch")
                col_preview1, col_preview2 = st.columns(2)
                
                with col_preview1:
                    st.markdown("**Trước khi làm sạch (Gốc):**")
                    st.dataframe(df.head(), use_container_width=True)
                    st.write(f"- Số dòng gốc: `{df.shape[0]}`")
                    st.write(f"- Số ô NaN còn lại: `{df.isna().sum().sum()}`")
                    
                with col_preview2:
                    st.markdown("**Sau khi làm sạch (Mới):**")
                    st.dataframe(df_cleaned.head(), use_container_width=True)
                    st.write(f"- Số dòng mới: `{df_cleaned.shape[0]}`")
                    st.write(f"- Số ô NaN còn lại: `{df_cleaned.isna().sum().sum()}`")
                
                # PHẦN 3: TẢI FILE DỮ LIỆU ĐÃ LÀM SẠCH VỀ MÁY
                st.markdown("---")
                st.subheader("📥 Tải xuống dữ liệu sạch")
                
                # Sửa lỗi Font Tiếng Việt khi mở trên Excel bằng cách sử dụng UTF-8-SIG (có chứa BOM)
                csv_data = df_cleaned.to_csv(index=False).encode('utf-8-sig')
                
                st.download_button(
                    label="🚀 Tải xuống tệp CSV đã làm sạch",
                    data=csv_data,
                    file_name="clean_data.csv",
                    mime="text/csv; charset=utf-8-sig",
                    key="download_clean_csv"
                )
                st.info("Bấm nút trên để tải ngay tệp tin đã được xử lý triệt để NaN về máy tính của bạn!")
                
            else:
                st.success("Bộ dữ liệu của bạn hoàn toàn sạch sẽ! Không cần thực hiện thao tác làm sạch dữ liệu khuyết thiếu.")
                
                st.markdown("---")
                st.subheader("📥 Tải xuống dữ liệu")
                csv_data = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="🚀 Tải xuống tệp CSV",
                    data=csv_data,
                    file_name="data.csv",
                    mime="text/csv; charset=utf-8-sig"
                )

        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi đọc tệp dữ liệu: {e}")
            st.info("Vui lòng đảm bảo tệp tin tải lên có định dạng CSV chuẩn mã hóa UTF-8.")
