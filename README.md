# FormE1 – Streamlit App (Stéphanie Parthenay)

Privacy-first Streamlit app to prepare UK Form E1 with:
- Statement parsing (bank/Revolut PDFs & screenshots → OCR fallback)
- Employment (Parasol weekly payslips)
- Property (Airbnb PDFs in EUR → GBP @ statement rate)
- Advanced visuals (Plotly), drill-downs, and exportable CSV/XLSX/PDF/PNG

## Quickstart
```bash
# from C:\Users\danie\MyApps\FormE1
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app/Home.py
