// Wait for DOM to load
document.addEventListener("DOMContentLoaded", () => {
  // ✅ Form Submission Alert
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      // e.preventDefault(); // Uncomment this if testing without backend
      console.log("Form submitted:", form.id || "unnamed");
    });
  });

  // ✅ Show/Hide Password Toggle
  const toggleBtns = document.querySelectorAll(".toggle-password");
  toggleBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = document.getElementById(btn.dataset.target);
      if (input.type === "password") {
        input.type = "text";
        btn.textContent = "Hide";
      } else {
        input.type = "password";
        btn.textContent = "Show";
      }
    });
  });

  // ✅ Success Flash Message Fade-Out
  const flash = document.querySelector(".flash-msg");
  if (flash) {
    setTimeout(() => {
      flash.style.display = "none";
    }, 3000);
  }

  // ✅ Highlight selected product on click
  const productCards = document.querySelectorAll(".product-card");
  productCards.forEach((card) => {
    card.addEventListener("click", () => {
      productCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
    });
  });
});
