import argparse
from pathlib import Path

import pandas as pd

from normalizers import normalize_phone

REQUIRED_COLUMNS = {"full_name", "phone", "email"}


def read_customer_file(input_file: Path) -> pd.DataFrame:
    suffix = input_file.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(input_file, dtype=str)

    if suffix == ".xlsx":
        return pd.read_excel(input_file, dtype=str)

    raise ValueError("Поддерживаются только файлы CSV и XLSX.")


def load_and_validate(input_file: Path) -> pd.DataFrame:
    data = read_customer_file(input_file).fillna("")

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(
            "В файле нет обязательных колонок: "
            f"{', '.join(sorted(missing_columns))}"
        )

    errors = []

    if (data["full_name"].str.strip() == "").any():
        errors.append("Есть пустые ФИО.")

    if (data["phone"].str.strip() == "").any():
        errors.append("Есть пустые телефоны.")

    normalized_phones = []
    for phone in data["phone"]:
        try:
            normalized_phones.append(normalize_phone(phone))
        except ValueError as error:
            errors.append(str(error))

    if not errors:
        data["phone"] = normalized_phones

    if data["phone"].duplicated().any():
        errors.append("Есть повторяющиеся телефоны.")

    if errors:
        raise ValueError("\n".join(errors))

    return data


if __name__ == "__main__":
    default_file = Path(__file__).resolve().parents[1] / "data" / "raw" / "customers.csv"

    parser = argparse.ArgumentParser(description="Проверка файла клиентов.")
    parser.add_argument("input_file", nargs="?", type=Path, default=default_file)
    arguments = parser.parse_args()

    customers = load_and_validate(arguments.input_file)

    print(f"Файл проверен: {arguments.input_file.name}")
    print(f"Строк клиентов: {len(customers)}")
    print(customers)
