from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "customer_phone",
    "manager_email",
    "service_name",
    "amount",
    "status",
    "closed_at",
    "paid_amount",
    "paid_at",
    "payment_method",
}
ALLOWED_STATUSES = {"proposal", "won", "lost"}


def is_valid_amount(value: str) -> bool:
    try:
        return Decimal(value) >= 0
    except InvalidOperation:
        return False


def load_and_validate(input_file: Path) -> pd.DataFrame:
    data = pd.read_csv(input_file, dtype=str).fillna("")

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(
            "В CSV нет обязательных колонок: "
            f"{', '.join(sorted(missing_columns))}"
        )

    errors = []

    for column in [
        "customer_phone",
        "manager_email",
        "service_name",
        "amount",
        "status",
    ]:
        if (data[column].str.strip() == "").any():
            errors.append(f"Есть пустые значения в колонке {column}.")

    unknown_statuses = set(data["status"]) - ALLOWED_STATUSES
    if unknown_statuses:
        errors.append(
            f"Неизвестные статусы сделок: {', '.join(sorted(unknown_statuses))}"
        )

    for index, row in data.iterrows():
        if not is_valid_amount(row["amount"]):
            errors.append(f"Строка {index + 2}: некорректная сумма сделки.")

        if row["paid_amount"] and not is_valid_amount(row["paid_amount"]):
            errors.append(f"Строка {index + 2}: некорректная сумма оплаты.")

        if row["paid_amount"] and not row["paid_at"]:
            errors.append(f"Строка {index + 2}: у оплаты отсутствует дата.")

        if row["paid_amount"] and not row["payment_method"]:
            errors.append(f"Строка {index + 2}: у оплаты отсутствует способ оплаты.")

        if row["status"] == "won" and not row["closed_at"]:
            errors.append(f"Строка {index + 2}: успешная сделка без даты закрытия.")

    if errors:
        raise ValueError("\n".join(errors))

    return data


if __name__ == "__main__":
    input_file = Path(__file__).resolve().parents[1] / "data" / "raw" / "deals.csv"
    deals = load_and_validate(input_file)

    print(f"Файл проверен: {input_file.name}")
    print(f"Строк сделок: {len(deals)}")
    print(deals)
