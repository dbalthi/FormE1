# Methodology (High-level)
- Ingestion: PDFs via pdfplumber/camelot/tabula; screenshots via Tesseract OCR.
- Normalisation: Schema → Transaction(date, desc, vendor, amount, currency, account).
- Classification: YAML keyword/regex + user overrides persisted in SQLite.
- Income: Parasol payslip parser → gross → deductions → net; rolling 12 months.
- Property: Airbnb statements → EUR→GBP (statement rate); occupancy; net.
- Evidence Pack: CSV/XLSX tables, PDF report, and chart images (PNG/PDF).
