document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('plan-form');
  const button = document.getElementById('generate-button');
  if (!form || !button) return;
  form.addEventListener('submit', (event) => {
    if (!form.reportValidity()) {
      event.preventDefault();
      return;
    }
    button.disabled = true;
    button.querySelector('.button-label').hidden = true;
    const loading = button.querySelector('.loading-label');
    loading.hidden = false;
    loading.style.display = 'inline-flex';
  });
});
