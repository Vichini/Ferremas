import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import Home from './home';         // Importa Home externo
import Dashboard from './dashboard'; // Usa el Dashboard separado
import Login from './login';       // Login separado

function App() {
  const [usuario, setUsuario] = useState(null);

  return (
    <Router>
      <nav style={{ marginBottom: '20px' }}>
        <Link to="/">Home</Link> |{' '}
        {usuario ? <Link to="/dashboard">Dashboard</Link> : <Link to="/login">Login</Link>}
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login setUsuario={setUsuario} />} />
        <Route path="/dashboard" element={<Dashboard usuario={usuario} setUsuario={setUsuario} />} />
      </Routes>
    </Router>
  );
}

export default App;
