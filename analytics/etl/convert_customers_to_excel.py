from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
CSV_FILE = PROJECT_DIR / "data" / "raw" / "customers.csv"
EXCEL_FILE = PROJECT_DIR / "data" / "raw" / "customers.xlsx"

customers = pd.read_csv(CSV_FILE, dtype=str)
customers.to_excel(EXCEL_FILE, index=False)

print(f"Создан Excel-файл: {EXCEL_FILE.name}")
print(f"Строк клиентов: {len(customers)}")
