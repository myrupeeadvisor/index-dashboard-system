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
def get_bse_pdf():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import requests

    base_url = "https://www.bseindices.com/Downloads/Equity_Index_Dashboard_"

    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)

        month = dt.strftime("%b")
        year = dt.strftime("%Y")

        url = f"{base_url}{month}_{year}.pdf"

        try:
            print("Trying BSE:", url)

            res = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )

            # 🔥 IMPORTANT FIX (same logic as NSE)
            if res.status_code == 200 and res.headers.get("Content-Type") == "application/pdf":

                with open("static/bse.pdf", "wb") as f:
                    f.write(res.content)

                return {
                    "pdf_url": "https://index-dashboard-system-1.onrender.com/static/bse.pdf",
                    "month": f"{month} {year}",
                    "source": "BSE"
                }

        except Exception as e:
            print("BSE error:", e)
            continue

    return {"error": "BSE PDF not available"}

# NSE
@app.get("/api/nse-pdf")
def get_nse_pdf():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import requests

    base_url = "https://www.niftyindices.com/Index_Dashboard/Index_Dashboard_"

    today = datetime.today()

    for i in range(2):
        dt = today - relativedelta(months=i)

        month = dt.strftime("%b").upper()
        year = dt.strftime("%Y")

        url = f"{base_url}{month}{year}.pdf"

        try:
            print("Trying NSE:", url)

            res = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )

            # 🔥 IMPORTANT FIX
            if res.status_code == 200 and res.headers.get("Content-Type") == "application/pdf":

                with open("static/nse.pdf", "wb") as f:
                    f.write(res.content)

                return {
                    "pdf_url": "https://index-dashboard-system-1.onrender.com/static/nse.pdf",
                    "month": f"{month} {year}",
                    "source": "NSE"
                }

        except Exception as e:
            print("Error:", e)
            continue

    return {"error": "NSE PDF not available"}
