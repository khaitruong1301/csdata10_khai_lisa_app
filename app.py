import streamlit as st
import pandas as pd
import openpyxl
st.set_page_config(
    page_title="LISASTORE Dashboard (Beginner)",
    layout="wide"
)

st.title("📊 Ứng dụng phân tích chuỗi cửa hàng mỹ phẩm LISASTORE")

# -----------------------------
# 1. HÀM LOAD DATA
# -----------------------------
@st.cache_data
def load_data(excel_file: str):
    df_store = pd.read_excel(excel_file, sheet_name="CuaHang",engine="openpyxl")
    df_nv = pd.read_excel(excel_file, sheet_name="NhanVien",engine="openpyxl")
    df_kh = pd.read_excel(excel_file, sheet_name="KhachHang",engine="openpyxl")
    df_sp = pd.read_excel(excel_file, sheet_name="SanPham",engine="openpyxl")
    df_dh = pd.read_excel(excel_file, sheet_name="DonHang",engine="openpyxl")

    # Chuyển cột Ngày sang kiểu datetime
    if "Ngay" in df_dh.columns:
        df_dh["Ngay"] = pd.to_datetime(df_dh["Ngay"], errors="coerce")

    return df_store, df_nv, df_kh, df_sp, df_dh


# -----------------------------
# 2. LOAD FILE EXCEL
# -----------------------------
excel_file = "./data_store_my_pham.xlsx"

try:
    df_store, df_nv, df_kh, df_sp, df_dh = load_data(excel_file)
except FileNotFoundError:
    st.error(f"Không tìm thấy file `{excel_file}`. Hãy chắc chắn file nằm cùng thư mục với app.py.")
    st.stop()

# -----------------------------
# 3. SIDEBAR
# -----------------------------
st.sidebar.header("🔧 Điều hướng")

page = st.sidebar.radio(
    "Chọn chức năng:",
    (
        "1. Xem dữ liệu",
        "2. Lọc đơn hàng",
        "3. Thống kê sản phẩm",
        "4. Khách hàng",
        "5. Dashboard đơn giản",
    )
)

st.sidebar.markdown("---")
st.sidebar.write("💡 Dành cho người mới bắt đầu Pandas + Streamlit")


# -----------------------------
# 4. TRANG 1: XEM DỮ LIỆU
# -----------------------------
if page == "1. Xem dữ liệu":
    st.subheader("📄 Xem dữ liệu các bảng")

    sheet_name = st.selectbox(
        "Chọn bảng dữ liệu:",
        ("CuaHang", "NhanVien", "KhachHang", "SanPham", "DonHang")
    )

    if sheet_name == "CuaHang":
        df = df_store
    elif sheet_name == "NhanVien":
        df = df_nv
    elif sheet_name == "KhachHang":
        df = df_kh
    elif sheet_name == "SanPham":
        df = df_sp
    else:
        df = df_dh

    st.write(f"**Bảng đang xem:** `{sheet_name}`")
    st.write(f"**Số dòng:** {df.shape[0]}  |  **Số cột:** {df.shape[1]}")

    st.dataframe(df, use_container_width=True)


# -----------------------------
# 5. TRANG 2: LỌC ĐƠN HÀNG
# -----------------------------
elif page == "2. Lọc đơn hàng":
    st.subheader("🧾 Lọc đơn hàng")

    col1, col2, col3 = st.columns(3)

    # --- Filter theo cửa hàng ---
    with col1:
        stores_options = ["Tất cả"] + df_store["MaCuaHang"].tolist()
        selected_store = st.selectbox("Chọn cửa hàng:", stores_options)

    # --- Filter theo ngày ---
    min_date = df_dh["Ngay"].min()
    max_date = df_dh["Ngay"].max()

    with col2:
        start_date = st.date_input(
            "Từ ngày:",
            value=min_date.date() if pd.notnull(min_date) else None
        )
    with col3:
        end_date = st.date_input(
            "Đến ngày:",
            value=max_date.date() if pd.notnull(max_date) else None
        )

    # --- Filter theo khoảng tiền ---
    st.markdown("### 💰 Lọc theo khoảng tiền")
    min_tien = int(df_dh["TongTien"].min())
    max_tien = int(df_dh["TongTien"].max())

    tien_min, tien_max = st.slider(
        "Chọn khoảng tiền (VNĐ):",
        min_value=min_tien,
        max_value=max_tien,
        value=(min_tien, max_tien),
        step=50000
    )

    # --- Áp dụng filter ---
    df_filtered = df_dh.copy()

    # Cửa hàng
    if selected_store != "Tất cả":
        df_filtered = df_filtered[df_filtered["MaCuaHang"] == selected_store]

    # Ngày
    df_filtered = df_filtered[
        (df_filtered["Ngay"] >= pd.to_datetime(start_date)) &
        (df_filtered["Ngay"] <= pd.to_datetime(end_date))
    ]

    # Khoảng tiền
    df_filtered = df_filtered[
        (df_filtered["TongTien"] >= tien_min) &
        (df_filtered["TongTien"] <= tien_max)
    ]

    st.markdown("### 📌 Kết quả lọc")

    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Số đơn hàng:** {df_filtered.shape[0]}")
    with col_b:
        st.write(f"**Tổng doanh thu (VNĐ):** {int(df_filtered['TongTien'].sum()):,}")

    st.dataframe(df_filtered, use_container_width=True)

    # Tùy chọn tải CSV
    csv_data = df_filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Tải kết quả lọc dưới dạng CSV",
        data=csv_data,
        file_name="don_hang_loc.csv",
        mime="text/csv"
    )


# -----------------------------
# 6. TRANG 3: THỐNG KÊ SẢN PHẨM
# -----------------------------
elif page == "3. Thống kê sản phẩm":
    st.subheader("💄 Thống kê sản phẩm")

    st.markdown("### 📋 Danh sách sản phẩm")
    st.dataframe(df_sp, use_container_width=True)

    st.markdown("### 📊 Thống kê nhanh")

    max_price_row = df_sp.loc[df_sp["Gia"].idxmax()]
    min_price_row = df_sp.loc[df_sp["Gia"].idxmin()]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Giá cao nhất (VNĐ)",
            value=f"{int(max_price_row['Gia']):,}",
            delta=max_price_row["TenSP"]
        )

    with col2:
        st.metric(
            label="Giá thấp nhất (VNĐ)",
            value=f"{int(min_price_row['Gia']):,}",
            delta=min_price_row["TenSP"]
        )

    with col3:
        st.metric(
            label="Giá trung bình (VNĐ)",
            value=f"{int(df_sp['Gia'].mean()):,}"
        )

    with col4:
        st.metric(
            label="Tổng tồn kho",
            value=int(df_sp["SoLuongTon"].sum())
        )


# -----------------------------
# 7. TRANG 4: KHÁCH HÀNG
# -----------------------------
elif page == "4. Khách hàng":
    st.subheader("👤 Tìm kiếm khách hàng")

    keyword = st.text_input("Nhập tên khách hàng (hoặc một phần tên):")

    if keyword:
        df_result = df_kh[df_kh["TenKH"].str.contains(keyword, case=False, na=False)]
        st.write(f"🔎 Tìm thấy **{df_result.shape[0]}** khách hàng phù hợp.")
        st.dataframe(df_result, use_container_width=True)

        # Cho phép chọn 1 khách hàng để xem chi tiết
        st.markdown("### 📌 Xem chi tiết khách hàng")

        kh_list = df_result["MaKH"].tolist()
        if kh_list:
            selected_kh = st.selectbox("Chọn mã khách hàng:", kh_list)
            kh_info = df_result[df_result["MaKH"] == selected_kh].iloc[0]

            st.write(f"**Mã KH:** {kh_info['MaKH']}")
            st.write(f"**Tên:** {kh_info['TenKH']}")
            st.write(f"**SĐT:** {kh_info['SoDT']}")
            st.write(f"**Email:** {kh_info['Email']}")
            st.write(f"**Địa chỉ:** {kh_info['DiaChi']}")
    else:
        st.info("Nhập từ khóa để bắt đầu tìm kiếm khách hàng.")


# -----------------------------
# 8. TRANG 5: DASHBOARD ĐƠN GIẢN
# -----------------------------
elif page == "5. Dashboard đơn giản":
    st.subheader("📈 Dashboard đơn giản")

    # --- Doanh thu theo cửa hàng ---
    st.markdown("### 💰 Doanh thu theo cửa hàng")

    revenue_by_store = df_dh.groupby("MaCuaHang")["TongTien"].sum().reset_index()
    # Gắn tên cửa hàng
    revenue_by_store = revenue_by_store.merge(df_store, on="MaCuaHang", how="left")

    st.dataframe(revenue_by_store[["MaCuaHang", "TenCuaHang", "TongTien"]])

    st.bar_chart(
        data=revenue_by_store,
        x="TenCuaHang",
        y="TongTien"
    )

    # --- Số lượng đơn theo tháng ---
    st.markdown("### 📅 Số lượng đơn hàng theo tháng")

    df_dh_valid = df_dh.dropna(subset=["Ngay"]).copy()
    df_dh_valid["YearMonth"] = df_dh_valid["Ngay"].dt.to_period("M").astype(str)

    orders_by_month = df_dh_valid.groupby("YearMonth")["MaDH"].count().reset_index()
    orders_by_month.rename(columns={"MaDH": "SoDon"}, inplace=True)

    st.dataframe(orders_by_month)

    st.line_chart(
        data=orders_by_month,
        x="YearMonth",
        y="SoDon"
    )
