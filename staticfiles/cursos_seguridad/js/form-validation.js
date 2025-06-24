document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('signupForm');
  if (!form) return;

  const username = form.username;
  const password1 = form.password1;
  const password2 = form.password2;

  const usernameError = document.getElementById('username-error');
  const password1Error = document.getElementById('password1-error');
  const password2Error = document.getElementById('password2-error');

  function validateUsername() {
    if (!username) return true;
    const val = username.value.trim();
    if (val === '') {
      username.classList.add('invalid');
      username.classList.remove('valid');
      usernameError.textContent = 'El nombre de usuario es obligatorio.';
      return false;
    } else if (val.length > 150) {
      username.classList.add('invalid');
      username.classList.remove('valid');
      usernameError.textContent = 'Máximo 150 caracteres.';
      return false;
    }
    username.classList.remove('invalid');
    username.classList.add('valid');
    usernameError.textContent = '';
    return true;
  }

  function validatePassword1() {
    if (!password1) return true;
    const val = password1.value;
    if (val.trim() === '') {
      password1.classList.add('invalid');
      password1.classList.remove('valid');
      password1Error.textContent = 'La contraseña es obligatoria.';
      return false;
    } else if (val.length < 8) {
      password1.classList.add('invalid');
      password1.classList.remove('valid');
      password1Error.textContent = 'La contraseña debe tener al menos 8 caracteres.';
      return false;
    }
    password1.classList.remove('invalid');
    password1.classList.add('valid');
    password1Error.textContent = '';
    return true;
  }

  function validatePassword2() {
    if (!password2) return true;
    const val = password2.value;
    if (val.trim() === '') {
      password2.classList.add('invalid');
      password2.classList.remove('valid');
      password2Error.textContent = 'Repetir la contraseña es obligatorio.';
      return false;
    } else if (val !== password1.value) {
      password2.classList.add('invalid');
      password2.classList.remove('valid');
      password2Error.textContent = 'Las contraseñas no coinciden.';
      return false;
    }
    password2.classList.remove('invalid');
    password2.classList.add('valid');
    password2Error.textContent = '';
    return true;
  }

  // Si viene error del backend, marcar inputs y mostrar texto
  const backendError = form.dataset.error;
  if (backendError) {
    if (username) username.classList.add('invalid');
    if (password1) password1.classList.add('invalid');
    if (password2) password2.classList.add('invalid');
    if (usernameError) usernameError.textContent = backendError;
    if (password1Error) password1Error.textContent = backendError;
    if (password2Error) password2Error.textContent = backendError;
  }

  // Validaciones en tiempo real
  if (username) username.addEventListener('input', validateUsername);
  if (password1) password1.addEventListener('input', () => {
    validatePassword1();
    validatePassword2();
  });
  if (password2) password2.addEventListener('input', validatePassword2);

  // Validar antes de enviar
  form.addEventListener('submit', function(event) {
    const validUser = validateUsername();
    const validPass1 = validatePassword1();
    const validPass2 = validatePassword2();
    if (!validUser || !validPass1 || !validPass2) {
      event.preventDefault();
    }
  });
});

