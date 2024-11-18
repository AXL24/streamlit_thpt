from pymongo import MongoClient
import pandas as pd

# Kết nối MongoDB
def connect_to_mongodb(uri, database_name):
    client = MongoClient("mongodb+srv://axellent2004:0964212618@bigdata.l07vk.mongodb.net/")
    return client["thpt"]

# Truy vấn dữ liệu theo điều kiện
def fetch_data(db, collection_name, year_filter=None):
    query = {}
    if year_filter:
        query = {"nam": {"$in": year_filter}}  # Lọc theo năm

    # Lấy chỉ các cột cần thiết
    projection = {
        "sbd": {"$toString": "$sbd"}, "toan": 1, "ngu_van": 1, "ngoai_ngu": 1,
        "vat_li": 1, "hoa_hoc": 1, "sinh_hoc": 1, "lich_su": 1,
        "dia_li": 1, "gdcd": 1, "_id": 0
    }

    # Truy vấn dữ liệu MongoDB
    records = db[collection_name].find(query, projection)
    df = pd.DataFrame(records)

    # Chuẩn hóa tên cột
    df.columns = df.columns.str.lower()
    if "sbd" in df.columns:
        columns = ["sbd"] + [col for col in df.columns if col != "sbd"]
        df = df[columns]
    return df
