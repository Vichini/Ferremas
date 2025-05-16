import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login({ setUsuario }) {
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [mensaje, setMensaje] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:5000/login', { correo, password });
      setUsuario({ correo, rol: res.data.rol });
      navigate('/dashboard');
    } catch (error) {
      setMensaje(error.response?.data?.mensaje || 'Error en login');
    }
  };

  return (
    <div>
      <h1>Iniciar sesión</h1>
      <form onSubmit={handleLogin}>
        <input type="email" placeholder="Correo" value={correo} onChange={e => setCorreo(e.target.value)} required />
        <br />
        <input type="password" placeholder="Contraseña" value={password} onChange={e => setPassword(e.target.value)} required />
        <br />
        <button type="submit">Ingresar</button>
      </form>
      {mensaje && <p style={{ color: 'red' }}>{mensaje}</p>}
    </div>
  );
}

export default Login;
