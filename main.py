from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import os

app = FastAPI()

# Allow frontend access
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

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return {"status": "API Running"}


# 🔽 COMMON DOWNLOAD FUNCTION
def download_and_save(url, filename):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=15)

        # Validate real PDF
        if res.status_code == 200 and len(res.content) > 50000:
            with open(f"static/{filename}", "wb") as f:
                f.write(res.content)
            return True
    except:
        return False

    return False


# 🔵 BSE API
@app.get("/api/bse-pdf")
def get_bse_pdf():
    base_url = "https://www.bseindices.com/Downloads/Equity_Index_Dashboard_"
    today = datetime.today()

    for i in range(2):  # current + previous month
        dt = today - relativedelta(months=i)

        month = dt.strftime("%b")
        year = dt.strftime("%Y")

        url = f"{base_url}{month}_{year}.pdf"

        if download_and_save(url, "bse.pdf"):
            return {
                "pdf_url": "https://index-dashboard-system.onrender.com/static/bse.pdf",
                "month": f"{month} {year}",
                "source": "BSE"
            }

    return {"error": "PDF not available"}


# 🔵 NSE API
@app.get("/api/nse-pdf")
def get_nse_pdf():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import requests

    base_url = "https://www.niftyindices.com/Index_Dashboard/Index_Dashboard_"
    headers = {"User-Agent": "Mozilla/5.0"}

    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)

month = dt.strftime("%b").upper()   # MAR
year = dt.strftime("%Y")            # 2026

url = f"{base_url}{month}{year}.pdf"

        try:
            res = requests.get(url, headers=headers, timeout=20)

            # 🔥 relaxed validation (important)
            if res.status_code == 200 and len(res.content) > 20000:
                with open("static/nse.pdf", "wb") as f:
                    f.write(res.content)

                return {
                    "pdf_url": "https://index-dashboard-system.onrender.com/static/nse.pdf",
                    "month": f"{month} {year}",
                    "source": "NSE"
                }

        except:
            continue

    return {"error": "PDF not available"}
