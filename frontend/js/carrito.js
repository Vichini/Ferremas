let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

const listaCarrito = document.getElementById('lista-carrito');
const totalCarrito = document.getElementById('total');
const btnVaciar = document.getElementById('vaciar-carrito');
const btnFinalizar = document.getElementById('finalizar-compra');

function guardarCarrito() {
  localStorage.setItem('carrito', JSON.stringify(carrito));
}

function mostrarCarrito() {
  if (!listaCarrito || !totalCarrito) return;

  listaCarrito.innerHTML = '';

  if (carrito.length === 0) {
    listaCarrito.innerHTML = '<li>El carrito está vacío.</li>';
    totalCarrito.textContent = '0.00';
  } else {
    carrito.forEach((producto, index) => {
      const li = document.createElement('li');
      li.classList.add('producto-carrito');
      li.innerHTML = `
        <span>${producto.nombre} - $${producto.precio.toFixed(2)} x ${producto.cantidad}</span>
        <button class="btn-eliminar" title="Eliminar producto">&times;</button>
      `;
      const btnEliminar = li.querySelector('button');
      btnEliminar.addEventListener('click', () => eliminarProducto(index));
      listaCarrito.appendChild(li);
    });

    const total = carrito.reduce((acc, prod) => acc + prod.precio * prod.cantidad, 0);
    totalCarrito.textContent = total.toFixed(2);
  }
}

function agregarProductoAlCarrito(producto) {
  const existe = carrito.find(p => p.id === producto.id);
  if (existe) {
    existe.cantidad++;
  } else {
    carrito.push({ ...producto, cantidad: 1 });
  }
  guardarCarrito();
  alert(`${producto.nombre} agregado al carrito.`);
}

function eliminarProducto(index) {
  if (index >= 0 && index < carrito.length) {
    carrito.splice(index, 1);
    guardarCarrito();
    mostrarCarrito();
  }
}

function vaciarCarrito() {
  carrito = [];
  guardarCarrito();
  mostrarCarrito();
}

async function enviarPedidoAlBackend(token) {
  try {
    const response = await fetch('http://localhost:5000/pedido', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ carrito })
    });

    const data = await response.json();

    if (response.ok) {
      alert('Compra finalizada correctamente. ¡Gracias!');
      vaciarCarrito();
    } else {
      alert('Error al finalizar compra: ' + (data.mensaje || 'Intenta nuevamente.'));
    }
  } catch (error) {
    console.error(error);
    alert('Error de conexión con el servidor.');
  }
}

function finalizarCompra() {
  const token = localStorage.getItem('token');
  if (!token) {
    alert('Debes iniciar sesión para finalizar la compra.');
    window.location.href = 'login.html';
    return;
  }
  if (carrito.length === 0) {
    alert('El carrito está vacío.');
    return;
  }

  enviarPedidoAlBackend(token);
}

if (btnVaciar) btnVaciar.addEventListener('click', vaciarCarrito);
if (btnFinalizar) btnFinalizar.addEventListener('click', finalizarCompra);

document.addEventListener('DOMContentLoaded', mostrarCarrito);

// Exportar la función para que esté disponible globalmente
window.agregarProductoAlCarrito = agregarProductoAlCarrito;
