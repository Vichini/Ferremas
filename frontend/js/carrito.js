let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
const listaCarrito = document.getElementById('lista-carrito');
const totalCarrito = document.getElementById('total');
const btnVaciar = document.getElementById('vaciar-carrito');
const btnFinalizar = document.getElementById('finalizar-compra');
const valorDolar = parseFloat(localStorage.getItem('valorDolar')) || 0;

function guardarCarrito() {
  localStorage.setItem('carrito', JSON.stringify(carrito));
}

function mostrarCarrito() {
  if (!listaCarrito || !totalCarrito) return;

  listaCarrito.innerHTML = '';

  if (carrito.length === 0) {
    listaCarrito.innerHTML = '<li>El carrito está vacío.</li>';
    totalCarrito.textContent = 'Total: $0.00 CLP / $0.00 USD';
  } else {
    carrito.forEach((producto, index) => {
      const precioUSD = valorDolar > 0 ? (producto.precio / valorDolar).toFixed(2) : "N/A";

      const li = document.createElement('li');
      li.classList.add('producto-carrito');
      li.innerHTML = `
        <span>${producto.nombre} - $${producto.precio.toFixed(2)} CLP / $${precioUSD} USD x ${producto.cantidad}</span>
        <button class="btn-eliminar" title="Eliminar producto">&times;</button>
      `;
      const btnEliminar = li.querySelector('button');
      btnEliminar.addEventListener('click', () => eliminarProducto(index));
      listaCarrito.appendChild(li);
    });

    const totalCLP = carrito.reduce((acc, prod) => acc + prod.precio * prod.cantidad, 0);
    const totalUSD = valorDolar > 0 ? (totalCLP / valorDolar).toFixed(2) : "N/A";
    totalCarrito.textContent = `Total: $${totalCLP.toFixed(2)} CLP / $${totalUSD} USD`;
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
  mostrarCarrito();
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
  
async function finalizarCompra() {
  console.log('Iniciando finalizarCompra...');
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

  try {
    console.log('Enviando pedido al backend...');
    const pedidoResponse = await fetch('http://127.0.0.1:5000/pedido', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ carrito })
    });

    console.log('Pedido response status:', pedidoResponse.status);
    const pedidoData = await pedidoResponse.json();
    console.log('Pedido data:', pedidoData);

    if (!pedidoResponse.ok) {
      alert('Error al crear el pedido: ' + (pedidoData.mensaje || 'Intenta nuevamente.'));
      return;
    }

    const pedidoId = pedidoData.pedido_id;
    const total = carrito.reduce((acc, prod) => acc + prod.precio * prod.cantidad, 0);
    console.log(`Pedido ID: ${pedidoId}, Total: ${total}`);

    console.log('Solicitando inicio de pago a Transbank...');
    const transbankResponse = await fetch('http://127.0.0.1:5000/transbank/iniciar_pago', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pedido_id: pedidoId, monto: total })
    });

    console.log('Transbank response status:', transbankResponse.status);
    const transbankData = await transbankResponse.json();
    console.log('Transbank data:', transbankData);

    if (!transbankResponse.ok) {
      alert('Error al iniciar pago: ' + (transbankData.mensaje || 'Intenta nuevamente.'));
      return;
    }

    console.log('Redirigiendo a Webpay...');
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = transbankData.url;

    const inputToken = document.createElement('input');
    inputToken.type = 'hidden';
    inputToken.name = 'token_ws';
    inputToken.value = transbankData.token;

    form.appendChild(inputToken);
    document.body.appendChild(form);
    form.submit();

  } catch (error) {
    console.error('Error en finalizarCompra:', error);
    alert('Error en la conexión con el servidor.');
  }
}


if (btnVaciar) btnVaciar.addEventListener('click', vaciarCarrito);
if (btnFinalizar) btnFinalizar.addEventListener('click', finalizarCompra);

document.addEventListener('DOMContentLoaded', mostrarCarrito);

window.agregarProductoAlCarrito = agregarProductoAlCarrito;
