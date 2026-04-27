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

def get_bse_pdf():
    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)
        month = dt.strftime("%b")
        year = dt.strftime("%Y")

        url = f"https://www.bseindices.com/Downloads/Equity_Index_Dashboard_{month}_{year}.pdf"

        try:
            res = requests.get(url)
            if res.status_code == 200:
                return res.content, url
        except:
            pass

    return None, None

def parse_pdf(pdf_bytes):
    rows = []
    headers = None

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                if not headers:
                    headers = table[0]
                    for row in table[1:]:
                        rows.append(row)
                else:
                    for row in table:
                        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    return df.fillna("")

@app.get("/api/bse-data")
def bse_data():
    pdf, source = get_bse_pdf()

    if not pdf:
        return {"error": "Data not available"}

    df = parse_pdf(pdf)

    return {
        "source": source,
        "last_updated": str(datetime.now()),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records")
    }
