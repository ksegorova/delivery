const burger = document.querySelector('.burger');
const nav = document.querySelector('.main-nav');
if (burger && nav) {
  burger.addEventListener('click', () => {
    const opened = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', String(opened));
  });
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(';').shift() : '';
}

const toast = document.getElementById('toast');
let toastTimer;
function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
}

document.querySelectorAll('.add-btn').forEach((button) => {
  button.addEventListener('click', async () => {
    const original = button.textContent;
    button.disabled = true;
    button.textContent = 'Добавляем…';
    try {
      const response = await fetch('/cart/add/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({dish_id: button.dataset.dishId})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Не удалось добавить блюдо');
      const counter = document.getElementById('cart-count');
      if (counter) counter.textContent = data.count;
      showToast(data.message);
      button.textContent = 'Добавлено ✓';
    } catch (error) {
      showToast(error.message);
      button.textContent = original;
    } finally {
      button.disabled = false;
      setTimeout(() => { if (button.isConnected) button.textContent = original; }, 1200);
    }
  });
});

document.querySelectorAll('.validate-form').forEach((form) => {
  form.addEventListener('submit', (event) => {
    let valid = true;
    form.querySelectorAll('[required]').forEach((field) => {
      if (!field.value.trim()) {
        valid = false;
        field.setAttribute('aria-invalid', 'true');
      } else field.removeAttribute('aria-invalid');
    });
    const email = form.querySelector('input[type="email"]');
    if (email && email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      valid = false;
      email.setAttribute('aria-invalid', 'true');
    }
    const phone = form.querySelector('input[name="phone"]');
    if (phone && phone.value && phone.value.replace(/\D/g, '').length < 10) {
      valid = false;
      phone.setAttribute('aria-invalid', 'true');
    }
    const longText = form.querySelector('textarea[maxlength]');
    if (longText && longText.value.length > Number(longText.maxLength)) {
      valid = false;
      longText.setAttribute('aria-invalid', 'true');
    }
    if (!valid) {
      event.preventDefault();
      showToast('Проверьте обязательные поля формы.');
      const first = form.querySelector('[aria-invalid="true"]');
      if (first) first.focus();
    }
  });
});
