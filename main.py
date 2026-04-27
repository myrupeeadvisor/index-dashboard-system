@app.get("/api/bse-pdf")
def get_bse_pdf_url():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import requests

    base_url = "https://www.bseindices.com/Downloads/Equity_Index_Dashboard_"

    today = datetime.today()

    for i in range(2):  # current + previous month
        dt = today - relativedelta(months=i)

        month = dt.strftime("%b")
        year = dt.strftime("%Y")

        url = f"{base_url}{month}_{year}.pdf"

        try:
            res = requests.head(url)
            if res.status_code == 200:
                return {
                    "pdf_url": url,
                    "month": f"{month} {year}"
                }
        except:
            continue

    return {"error": "PDF not available"}


@app.get("/api/nse-pdf")
def get_nse_pdf_url():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import requests

    base_url = "https://www.niftyindices.com/Index_Dashboard/Index_Dashboard_"

    today = datetime.today()

    for i in range(2):  # current + previous month
        dt = today - relativedelta(months=i)

        month = dt.strftime("%b").upper()
        year = dt.strftime("%Y")

        url = f"{base_url}{month}{year}.pdf"

        try:
            res = requests.head(url)
            if res.status_code == 200:
                return {
                    "pdf_url": url,
                    "month": f"{month} {year}"
                }
        except:
            continue

    return {"error": "PDF not available"}
