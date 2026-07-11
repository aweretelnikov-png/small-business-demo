import load_customers
import load_deals
import load_leads


def main() -> None:
    print("=== Загрузка клиентов ===")
    load_customers.main(load_customers.DEFAULT_INPUT_FILE)

    print("\n=== Загрузка заявок ===")
    load_leads.main()

    print("\n=== Загрузка сделок и оплат ===")
    load_deals.main()

    print("\nETL-обновление завершено успешно.")


if __name__ == "__main__":
    main()
