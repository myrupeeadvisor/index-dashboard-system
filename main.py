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
        rows = []
        headers = None

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                table = page.extract_table()

                if not table or len(table) < 2:
                    continue

                if not headers:
                    headers = table[0]
                    for row in table[1:]:
                        if len(row) == len(headers):
                            rows.append(row)
                else:
                    for row in table:
                        if len(row) == len(headers):
                            rows.append(row)

        if not rows or not headers:
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=headers)
        return df.fillna("")

    except Exception as e:
        print("Parsing Error:", str(e))
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
