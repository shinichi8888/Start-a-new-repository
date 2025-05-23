import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from logic import evaluate_project
from fpdf import FPDF
import io

st.set_page_config(page_title="不動産収益シミュレーター", layout="centered")

st.title("💰 簡易 不動産収支シミュレーター")

# 入力欄
col1, col2 = st.columns(2)
with col1:
    land_price = st.number_input("土地取得費（万円）", 1000, 100000, 8000)
    construction = st.number_input("建築費（万円）", 1000, 200000, 14000)
    other = st.number_input("その他費用（万円）", 0, 5000, 1000)

with col2:
    rent = st.number_input("年間家賃収入（万円）", 100, 50000, 1200)
    vacancy = st.slider("空室率（％）", 0, 50, 10) / 100
    opex = st.slider("運営費率（％）", 0, 50, 20) / 100

# 建築条件入力
floor_ratio = st.number_input("容積率（％）", 100, 400, 200)
land_area = st.number_input("土地面積（㎡）", 100, 10000, 500)

# 物件タイプ別
type = st.selectbox("物件タイプ", ["アパート", "旅館", "ビル", "民泊"])

if type == "ビル":
    st.markdown("### 🏢 ビルモデル入力")
    floor_count = st.number_input("階数", 1, 20, 5)
    unit_per_floor = st.number_input("1フロアあたりの区画数", 1, 10, 3)
    rent_per_unit = st.number_input("1区画あたりの月額賃料（万円）", 5, 100, 20)
    rent = floor_count * unit_per_floor * rent_per_unit * 12

elif type == "民泊":
    st.markdown("### 🛏️ 民泊モデル入力")
    nights = st.number_input("年間稼働日数", 100, 365, 250)
    price_per_night = st.number_input("1泊単価（円）", 3000, 30000, 12000)
    rooms = st.number_input("部屋数", 1, 20, 4)
    occupancy_rate = st.slider("稼働率（％）", 0, 100, 70) / 100
    rent = rooms * nights * price_per_night * occupancy_rate / 10000  # 万円換算

# CSVアップロード（任意）
uploaded = st.file_uploader("物件CSVをアップロード（任意）", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    st.write(df.head())
    for i, row in df.iterrows():
        st.write(f"物件 {i+1}")
        res = evaluate_project(
            row["land_price"],
            row["construction"],
            row["other"],
            row["rent"],
            row["vacancy"],
            row["opex"]
        )
        st.write(res)

# 試算ボタン
if st.button("📊 試算する"):
    res = evaluate_project(
        land_price, construction, other, rent, vacancy, opex
    )
    st.subheader("📈 結果")
    st.write(res)

    # グラフ
    cash_flows = [- (land_price + construction + other)] + [res["NOI（万円）"]] * 20
    cash_flows[-1] += land_price * 0.9
    fig, ax = plt.subplots()
    ax.bar(range(1, 22), cash_flows)
    st.pyplot(fig)

    # CSVダウンロード
    df_result = pd.DataFrame([res])
    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button("📥 結果をCSVでダウンロード", csv, "result.csv", "text/csv")

    # PDF生成
    def generate_pdf(res_dict):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "収益シミュレーション結果", ln=True, align='C')
        for k, v in res_dict.items():
            pdf.cell(200, 10, f"{k}: {v}", ln=True)
        filename = "result.pdf"
        pdf.output(filename)
        return filename

    if st.button("📄 PDF見積書を生成"):
        filename = generate_pdf(res)
        with open(filename, "rb") as f:
            st.download_button("📎 PDFをダウンロード", f, file_name="見積書.pdf")

# 用途判定
if land_area > 1000 and floor_ratio > 300:
    st.success("🏨 この土地はホテル開発に適しています")
elif land_area > 300:
    st.info("🏠 中規模アパートまたは戸建て用地に適しています")
