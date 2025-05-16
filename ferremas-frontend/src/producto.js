import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Productos() {
  const [productos, setProductos] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get('http://localhost:000/productos')
      .then(res => setProductos(res.data))
      .catch(() => setError('Error al cargar los productos'));
  }, []);

  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Catálogo de Productos</h2>
      <ul>
        {productos.map(p => (
          <li key={p.id}>
            <strong>{p.nombre}</strong> — {p.descripcion} — ${p.precio} — Stock: {p.stock}
          </li>
        ))}z
      </ul>
    </div>
  );
}

export default Productos;
