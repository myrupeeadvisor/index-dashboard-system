from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, io
import pdfplumber
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API is running successfully"}

# ✅ SAFE PDF FETCH
def get_bse_pdf():
    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)
        month = dt.strftime("%b")
        year = dt.strftime("%Y")

        url = f"https://www.bseindices.com/Downloads/Equity_Index_Dashboard_{month}_{year}.pdf"

        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res.content, url
        except:
            continue

    return None, None

# ✅ SAFE PARSER (NO CRASH)
def parse_pdf(pdf_bytes):
    try:
        import re

        text = ""

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

        lines = text.split("\n")

        data = []

        for line in lines:
            # Identify valid index rows (contain % values multiple times)
            if line.count("%") >= 5:
                parts = re.split(r"\s+", line.strip())

                if len(parts) < 12:
                    continue

                try:
                    row = {
                        "Index": " ".join(parts[:-11]),
                        "1M": parts[-11],
                        "YTD": parts[-10],
                        "1Yr": parts[-9],
                        "3Yr": parts[-8],
                        "5Yr": parts[-7],
                        "10Yr": parts[-6],
                        "Risk_1Yr": parts[-5],
                        "RiskAdj_1Yr": parts[-4],
                        "PE": parts[-3],
                        "PB": parts[-2],
                        "DivYield": parts[-1],
                    }
                    data.append(row)

                except:
                    continue

        return pd.DataFrame(data)

    except Exception as e:
        print("Final Parser Error:", str(e))
        return pd.DataFrame()

@app.get("/api/bse-data")
def bse_data():
    try:
        pdf, source = get_bse_pdf()

        if not pdf:
            return {"error": "PDF not found"}

        df = parse_pdf(pdf)

        if df.empty:
            return {"error": "No table data extracted"}

        return {
            "source": source,
            "last_updated": str(datetime.now()),
            "columns": list(df.columns),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        return {"error": str(e)}
