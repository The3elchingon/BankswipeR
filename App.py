
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for PDF parsing
import pytesseract
from PIL import Image
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="Bank Swipe Categorizer", layout="wide")
st.title("📊 Bank Swipe Categorizer")

uploaded_file = st.file_uploader("Upload a bank statement (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_transactions(text):
    lines = text.strip().split("\n")
    transactions = []
    for line in lines:
        if any(char.isdigit() for char in line):
            parts = line.split()
            try:
                date = datetime.strptime(parts[0], "%m/%d/%Y")
                amount = float(parts[-1].replace("$", "").replace(",", ""))
                description = " ".join(parts[1:-1])
                transactions.append({
                    "Date": date,
                    "Description": description,
                    "Amount": amount,
                    "Category": "Uncategorized"
                })
            except:
                continue
    return pd.DataFrame(transactions)

if uploaded_file:
    file_ext = os.path.splitext(uploaded_file.name)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    if file_ext == ".pdf":
        text = extract_text_from_pdf(tmp_path)
    else:
        image = Image.open(tmp_path)
        text = extract_text_from_image(image)

    transactions_df = parse_transactions(text)

    if not transactions_df.empty:
        st.session_state["transactions"] = transactions_df

if "transactions" in st.session_state:
    df = st.session_state["transactions"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👈 Swipe Left = Personal")
    with col2:
        st.markdown("### 👉 Swipe Right = Business")

    for i in range(len(df)):
        col1, col2, col3 = st.columns([3, 2, 3])
        col1.markdown(f"**{df.iloc[i]['Date'].strftime('%m/%d/%Y')}** - {df.iloc[i]['Description']}")
        col2.markdown(f"${df.iloc[i]['Amount']:.2f}")
        category = col3.radio(f"Categorize row {i+1}", ["Uncategorized", "Personal", "Business"], key=f"cat_{i}")
        df.at[i, "Category"] = category

    # Export
    st.markdown("### 📤 Export Categorized Transactions")
    if st.button("Export to Excel"):
        df = df.sort_values(by="Date")
        out_path = "/mnt/data/categorized_transactions.xlsx"
        df.to_excel(out_path, index=False)
        st.success("Exported successfully!")
        st.download_button("Download Excel", data=open(out_path, "rb"), file_name="categorized_transactions.xlsx")
