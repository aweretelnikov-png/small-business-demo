from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"full_name", "phone", "email"}


def load_and_validate(input_file: Path) -> pd.DataFrame:
    data = pd.read_csv(input_file, dtype=str).fillna("")

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
           raise ValueError(
               f"В CSV нет обязательных колонок: {', '.join(sorted(missing_columns))}"
           )

    errors = []

    if (data["full_name"].str.strip() == "").any():
           errors.append("Есть пустые ФИО.")

    if (data["phone"].str.strip() == "").any():
           errors.append("Есть пустые телефоны.")

    if data["phone"].duplicated().any():
           errors.append("Есть повторяющиеся телефоны.")

    if errors:
        raise ValueError("\n".join(errors))

    return data


if __name__ == "__main__":
       input_file = (
           Path(__file__).resolve().parents[1] / "data" / "raw" / "customers.csv"
       )
       customers = load_and_validate(input_file)

       print(f"Файл проверен: {input_file.name}")
       print(f"Строк клиентов: {len(customers)}")
       print(customers)