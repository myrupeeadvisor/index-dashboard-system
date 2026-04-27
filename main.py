from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os
import requests
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

# Ensure static folder exists
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"status": "API Running"}

def download_file(url, filename):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)

        if r.status_code == 200 and len(r.content) > 20000:
            with open(f"static/{filename}", "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        print("Download error:", e)

    return False


# BSE
@app.get("/api/bse-pdf")
def bse():
    base = "https://www.bseindices.com/Downloads/Equity_Index_Dashboard_"
    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)
        m = dt.strftime("%b")
        y = dt.strftime("%Y")

        url = f"{base}{m}_{y}.pdf"

        if download_file(url, "bse.pdf"):
            return {
                "pdf_url": "https://index-dashboard-system.onrender.com/static/bse.pdf",
                "month": f"{m} {y}",
                "source": "BSE"
            }

    return {"error": "BSE PDF not available"}


# NSE
@app.get("/api/nse-pdf")
def nse():
    base = "https://www.niftyindices.com/Index_Dashboard/Index_Dashboard_"
    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)
        m = dt.strftime("%b").upper()
        y = dt.strftime("%Y")

        url = f"{base}{m}{y}.pdf"

        if download_file(url, "nse.pdf"):
            return {
                "pdf_url": "https://index-dashboard-system.onrender.com/static/nse.pdf",
                "month": f"{m} {y}",
                "source": "NSE"
            }

    return {"error": "NSE PDF not available"}
