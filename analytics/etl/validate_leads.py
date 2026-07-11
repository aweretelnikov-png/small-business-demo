from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "customer_phone",
    "manager_email",
    "source",
    "service_name",
    "status",
    "desired_date",
    "comment",
}

ALLOWED_STATUSES = {"new", "contacted", "proposal", "closed"}


def load_and_validate(input_file: Path) -> pd.DataFrame:
    data = pd.read_csv(input_file, dtype=str).fillna("")

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"В CSV нет обязательных колонок: {', '.join(sorted(missing_columns))}"
        )

    errors = []

    for column in ["customer_phone", "manager_email", "source", "service_name",
 "status"]:
        if (data[column].str.strip() == "").any():
            errors.append(f"Есть пустые значения в колонке {column}.")

    unknown_statuses = set(data["status"]) - ALLOWED_STATUSES
    if unknown_statuses:
        errors.append(
            f"Неизвестные статусы: {', '.join(sorted(unknown_statuses))}"
        )

    invalid_dates = pd.to_datetime(
        data["desired_date"],
        format="%Y-%m-%d",
        errors="coerce",
    ).isna()

    if invalid_dates.any():
        errors.append("Есть даты не в формате ГГГГ-ММ-ДД.")

    if errors:
        raise ValueError("\n".join(errors))

    return data


if __name__ == "__main__":
    input_file = (
        Path(__file__).resolve().parents[1] / "data" / "raw" / "leads.csv"
    )
    leads = load_and_validate(input_file)

    print(f"Файл проверен: {input_file.name}")
    print(f"Строк заявок: {len(leads)}")
    print(leads)