document.getElementById('form-login').addEventListener('submit', async function(e) {
  e.preventDefault();

  const correo = document.getElementById('login-correo').value.trim();
  const password = document.getElementById('login-password').value;
  const mensaje = document.getElementById('login-error');

  mensaje.textContent = ''; // limpiar mensaje

  try {
    const res = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ correo, password })
    });

    const data = await res.json();

    if (res.ok) {
      // Guardar token y usuario en localStorage
      localStorage.setItem('token', data.token);
      localStorage.setItem('usuario', JSON.stringify({ correo, rol: data.rol || 'usuario' }));

      window.location.href = 'index.html'; // o la página que quieras
    } else {
      mensaje.textContent = data.mensaje || 'Credenciales inválidas';
    }
  } catch (error) {
    mensaje.textContent = 'Error al conectar con el servidor';
    console.error(error);
  }
});
