document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      button.textContent = "Copied";
      setTimeout(() => { button.textContent = "Copy"; }, 2000);
    } catch {
      button.textContent = "Copy unavailable";
    }
  });
});
