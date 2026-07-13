const form = document.querySelector("#lead-form");
const result = document.querySelector("#form-result");

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const lead = {
    name: formData.get("name").trim(),
    phone: formData.get("phone").trim(),
    service: formData.get("service"),
    district: formData.get("district").trim(),
    desired_date: formData.get("desired_date") || null,
    comment: formData.get("comment").trim() || null,
    consent: formData.get("consent") === "on",
  };

  console.log("Тестовая заявка:", lead);
  result.textContent = "Данные формы собраны. Отправку на сервер подключим следующим этапом.";
});
