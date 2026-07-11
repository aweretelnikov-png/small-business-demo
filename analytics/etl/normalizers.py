import re


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)

    if len(digits) == 10:
        digits = "7" + digits
    elif len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    if len(digits) != 11 or not digits.startswith("7"):
        raise ValueError(f"Некорректный российский телефон: {phone}")

    return f"+{digits}"


if __name__ == "__main__":
    examples = [
        "+7 999 123-45-67",
        "8 (999) 123-45-67",
        "79991234567",
    ]

    for example in examples:
        print(f"{example} -> {normalize_phone(example)}")
