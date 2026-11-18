document.querySelectorAll("[data-copy], [data-copy-target]").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      const text = button.dataset.copy ?? document.getElementById(button.dataset.copyTarget).textContent;
      await navigator.clipboard.writeText(text);
      button.textContent = "Copied";
      setTimeout(() => { button.textContent = "Copy"; }, 2000);
    } catch {
      button.textContent = "Copy unavailable";
    }
  });
});
