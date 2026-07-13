const form = document.querySelector("#lead-form");
const result = document.querySelector("#form-result");
const submitButton = form.querySelector('button[type="submit"]');

form.addEventListener("submit", async (event) => {
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

  submitButton.disabled = true;
  result.textContent = "Отправляем заявку…";

  try {
    const response = await fetch("http://localhost:8000/api/leads", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(lead),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error("Сервер отклонил данные заявки");
    }

    result.textContent = `Заявка №${data.lead_id} принята.`;
    form.reset();
  } catch (error) {
    console.error(error);
    result.textContent = "Не удалось отправить заявку. Попробуйте ещё раз.";
  } finally {
    submitButton.disabled = false;
  }
});
