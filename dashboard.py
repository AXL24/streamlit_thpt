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
    data_2022["year"] = 2022  # Thêm cột "year"
    
    data_2023 = fetch_data(db, "2023")  # Kết quả là một DataFrame
    data_2023["year"] = 2023  # Thêm cột "year"
    
    data_2024 = fetch_data(db, "2024")  # Kết quả là một DataFrame
    data_2024["year"] = 2024  # Thêm cột "year"
    
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
    years = st.sidebar.multiselect("Chọn năm", [2022, 2023, 2024], default=[2022, 2023, 2024])
    subjects = st.sidebar.multiselect(
        "Chọn môn học",
        ["toan", "ngu_van", "ngoai_ngu", "vat_li", "hoa_hoc", "sinh_hoc", "lich_su", "dia_li", "gdcd"],
        default=["toan", "ngu_van"]
    )

    # Lọc dữ liệu theo năm
    filtered_data = combined_data[combined_data["year"].isin(years)]
    
    # Hiển thị bảng dữ liệu
    st.subheader("Dữ liệu đã lọc")
    st.write(f"Tổng số bản ghi: {len(filtered_data)}")
    st.dataframe(filtered_data.head(100))  # Hiển thị 100 bản ghi đầu tiên

    # Phân tích điểm trung bình theo môn học
    if not filtered_data.empty:
        st.subheader("Điểm trung bình theo môn học của năm đã chọn")
        avg_scores = filtered_data[subjects].mean().reset_index()
        avg_scores.columns = ["Subject", "Average Score"]
        st.write(avg_scores)

        # Biểu đồ điểm trung bình
        fig_avg = px.bar(avg_scores, x="Subject", y="Average Score", title="Điểm trung bình theo môn học của năm đã chọn")
        st.plotly_chart(fig_avg)

        # Phân phối điểm
        st.subheader("Phân phối điểm")
        for subject in subjects:
            fig_dist = px.histogram(filtered_data, x=subject, nbins=20, title=f"Phân phối điểm {subject} của năm đã chọn")
            st.plotly_chart(fig_dist)

        # Xu hướng điểm qua các năm
        st.subheader("Xu hướng điểm qua các năm đã chọn")
        trend_data = filtered_data.groupby(["year"])[subjects].mean().reset_index()
        trend_data = pd.melt(trend_data, id_vars=["year"], var_name="Subject", value_name="Average Score")
        fig_trend = px.line(trend_data, x="year", y="Average Score", color="Subject", title="Xu hướng điểm theo năm")
        st.plotly_chart(fig_trend)

if __name__ == "__main__":
    main()
