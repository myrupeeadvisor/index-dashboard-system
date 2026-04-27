from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests

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
    return {"status": "API Running"}

# 🔵 BSE API
@app.get("/api/bse-pdf")
def get_bse_pdf():
    base_url = "https://www.bseindices.com/Downloads/Equity_Index_Dashboard_"
    headers = {"User-Agent": "Mozilla/5.0"}

    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)
        month = dt.strftime("%b")
        year = dt.strftime("%Y")

        url = f"{base_url}{month}_{year}.pdf"

        try:
            res = requests.get(url, headers=headers, timeout=10)

            if res.status_code == 200 and len(res.content) > 50000:
                return {
                    "pdf_url": url,
                    "month": f"{month} {year}",
                    "source": "BSE"
                }
        except:
            continue

    return {"error": "PDF not available"}


# 🔵 NSE API
@app.get("/api/nse-pdf")
def get_nse_pdf():
    base_url = "https://www.niftyindices.com/Index_Dashboard/Index_Dashboard_"
    headers = {"User-Agent": "Mozilla/5.0"}

    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)
        month = dt.strftime("%b").upper()
        year = dt.strftime("%Y")

        url = f"{base_url}{month}{year}.pdf"

        try:
            res = requests.get(url, headers=headers, timeout=10)

            if res.status_code == 200 and len(res.content) > 50000:
                return {
                    "pdf_url": url,
                    "month": f"{month} {year}",
                    "source": "NSE"
                }
        except:
            continue

    return {"error": "PDF not available"}
