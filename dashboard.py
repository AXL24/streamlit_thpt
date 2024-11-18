import streamlit as st
from merge import connect_to_mongodb, fetch_data
import pandas as pd
import plotly.express as px

# Kết nối MongoDB
MONGO_URI = "mongodb+srv://axellent2004:0964212618@bigdata.l07vk.mongodb.net/"  # Thay bằng MongoDB URI của bạn
DATABASE_NAME = "thpt"

# Caching để tăng hiệu suất
@st.cache_data
def load_data():
    # Kết nối tới MongoDB
    db = connect_to_mongodb(MONGO_URI, DATABASE_NAME) 
    
    # Tải dữ liệu từ 2 collection năm 2023 và 2024
    data_2022 = fetch_data(db, "2022")  # Kết quả là một DataFrame
    data_2022["nam"] = 2022  # Thêm cột "year"
    
    data_2023 = fetch_data(db, "2023")  # Kết quả là một DataFrame
    data_2023["nam"] = 2023  # Thêm cột "year"
    
    data_2024 = fetch_data(db, "2024")  # Kết quả là một DataFrame
    data_2024["nam"] = 2024  # Thêm cột "year"
    
    # Kết hợp dữ liệu
    combined_data = pd.concat([data_2022, data_2023, data_2024], ignore_index=True)
    return combined_data

# Tạo ứng dụng Streamlit
def main():
    st.title("Phân Tích Điểm THPT - 2023 & 2024\nsử dụng cloud mongodb")
    
    # Tải dữ liệu
    with st.spinner("Đang tải dữ liệu..."):
        combined_data = load_data()
    
    # Sidebar: Bộ lọc
    st.sidebar.header("Bộ lọc")
    cac_nam = st.sidebar.multiselect("Chọn năm", [2022, 2023, 2024], default=[2022, 2023, 2024])
    cac_mon = st.sidebar.multiselect(
        "Chọn môn học",
        ["toan", "ngu_van", "ngoai_ngu", "vat_li", "hoa_hoc", "sinh_hoc", "lich_su", "dia_li", "gdcd"],
        default=["toan", "ngu_van"]
    ) 
     # Search by roll number
    st.sidebar.header("Tìm kiếm thí sinh")
    selected_year = st.sidebar.selectbox("Chọn năm để tìm kiếm", [2022, 2023, 2024])
    roll_number = st.sidebar.text_input("Nhập số báo danh")

    # Lọc dữ liệu theo năm
    filtered_data = combined_data[combined_data["nam"].isin(cac_nam)]
    
    # Hiển thị bảng dữ liệu
    st.subheader("Dữ liệu đã lọc")
    st.write(f"Tổng số bản ghi: {len(filtered_data)}")
    st.dataframe(filtered_data.head(100))  # Hiển thị 100 bản ghi đầu tiên
    if roll_number:
        search_results = combined_data[(combined_data["nam"] == selected_year) & 
                                       (combined_data["sbd"] == roll_number)]
        
        if not search_results.empty:
            st.write(f"Kết quả tìm kiếm cho số báo danh: {roll_number} năm {selected_year}")
            st.dataframe(search_results)
        else:
            st.warning(f"Không tìm thấy kết quả cho số báo danh: {roll_number} năm {selected_year}")




    # Phân tích điểm trung bình theo môn học
    if not filtered_data.empty:
        # Search functionality
        st.subheader("Tìm kiếm theo số báo danh")
   


        st.subheader("Điểm trung bình theo môn học của năm đã chọn")
        trung_binh = filtered_data[cac_mon].mean().reset_index()
        trung_binh.columns = ["Môn", "Điểm trung bình"]
        st.write(trung_binh)

        # Biểu đồ điểm trung bình
        fig_avg = px.bar(trung_binh, x="Môn", y="Điểm trung bình", title="Điểm trung bình theo môn học")
        st.plotly_chart(fig_avg)

        # Phân phối điểm
        st.subheader("Phân phối điểm")
        for mon in cac_mon:
            fig_dist = px.histogram(filtered_data, x=mon, nbins=20, title=f"Phân phối điểm {mon} của năm đã chọn")
            st.plotly_chart(fig_dist)

        # Xu hướng điểm qua các năm
        st.subheader("Xu hướng điểm qua các năm đã chọn")
        xu_huong = filtered_data.groupby(["nam"])[cac_mon].mean().reset_index()
        xu_huong = pd.melt(xu_huong, id_vars=["nam"], var_name="mon", value_name="Điểm trung bình")
        fig_trend = px.line(xu_huong, x="nam", y="Điểm trung bình", color="mon", title="Xu hướng điểm theo năm")
        st.plotly_chart(fig_trend)

    
if __name__ == "__main__":
    main()
