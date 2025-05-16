import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [rol, setRol] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:5000/login', {
        correo,
        password,
      });
      setMensaje(res.data.mensaje);
      setRol(res.data.rol);
      setLoggedIn(true);
    } catch (error) {
      setMensaje(error.response?.data?.mensaje || 'Error en login');
    }
  };

  if (loggedIn) {
    return (
      <div>
        <h2>Bienvenido, {correo}</h2>
        <p>Tu rol es: {rol}</p>
        {/* Aquí podemos mostrar más según el rol */}
      </div>
    );
  }

  return (
    <div>
      <h2>Login FERREMAS</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Correo"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          required
        />
        <br />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <br />
        <button type="submit">Iniciar sesión</button>
      </form>
      {mensaje && <p>{mensaje}</p>}
    </div>
  );
}

export default App;
