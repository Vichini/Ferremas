import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import Productos from './Productos'; // importa tu componente Productos

function Dashboard({ usuario, setUsuario }) {
  const [verProductos, setVerProductos] = useState(false);

  if (!usuario) {
    return <Navigate to="/login" />;
  }

  const handleLogout = () => {
    setUsuario(null);
  };

  return (
    <div>
      <h2>Bienvenido, {usuario.correo}</h2>
      <p>Tu rol es: {usuario.rol}</p>
      <button onClick={() => setVerProductos(!verProductos)}>
        {verProductos ? 'Ocultar productos' : 'Ver productos'}
      </button>
      <button onClick={handleLogout}>Cerrar sesión</button>

      {verProductos && <Productos />}
    </div>
  );
}

export default Dashboard;
