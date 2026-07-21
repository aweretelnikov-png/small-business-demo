const form = document.querySelector("#lead-form");
const result = document.querySelector("#form-result");
const submitButton = form.querySelector('button[type="submit"]');
const desiredDate = document.querySelector("#desired-date");

desiredDate.min = new Date().toISOString().split("T")[0];

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (!reducedMotion && "IntersectionObserver" in window) {
  document.documentElement.classList.add("motion-ready");

  const revealGroups = [
    ".facts > div",
    ".section-heading",
    ".service-card",
    ".process-list article",
    ".price-section > *",
    ".request-copy",
    "#lead-form",
  ];

  const revealTargets = document.querySelectorAll(revealGroups.join(","));
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.12,
      rootMargin: "0px 0px -48px",
    },
  );

  revealTargets.forEach((target, index) => {
    target.classList.add("motion-reveal");
    target.style.setProperty("--reveal-delay", `${(index % 4) * 55}ms`);
    observer.observe(target);
  });
}

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
