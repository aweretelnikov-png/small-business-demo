const form = document.querySelector("#lead-form");
const result = document.querySelector("#form-result");
const submitButton = form.querySelector('button[type="submit"]');
const desiredDate = document.querySelector("#desired-date");

desiredDate.min = new Date().toISOString().split("T")[0];

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  result.className = "";

  if (!form.reportValidity()) {
    result.textContent = "Проверьте обязательные поля формы.";
    result.className = "error";
    return;
  }

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
  submitButton.textContent = "Отправляем...";
  result.textContent = "Сохраняем заявку и уведомляем менеджера.";

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
      const serverMessage = data?.detail?.[0]?.msg;
      throw new Error(serverMessage || "Сервер отклонил данные заявки");
    }

    result.textContent = `Заявка №${data.lead_id} принята. Менеджер получил уведомление.`;
    result.className = "success";
    form.reset();
  } catch (error) {
    console.error(error);
    result.textContent = error.message || "Не удалось отправить заявку. Попробуйте ещё раз.";
    result.className = "error";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Отправить заявку";
  }
});
