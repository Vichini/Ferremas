import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function Home() {
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get('http://localhost:5000/productos')
      .then(res => setProductos(res.data))
      .catch(() => setError('Error al cargar productos'));
  }, []);

  return (
    <div>
      <h1>Bienvenido a FERREMAS</h1>
      <Link to="/login">Iniciar sesión</Link>

      <h2>Catálogo de productos</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <ul>
        {productos.length === 0 && <li>No hay productos disponibles</li>}
        {productos.map(p => (
          <li key={p.id}>
            <strong>{p.nombre}</strong> — {p.descripcion} — ${p.precio} — Stock: {p.stock}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Home;
