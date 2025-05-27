document.addEventListener('DOMContentLoaded', () => {
  const contenedorListado = document.getElementById('productos-listado');
  const contenedorDestacados = document.getElementById('destacados');

  fetch('http://localhost:5000/productos')
    .then(res => res.json())
    .then(data => {
      if (data.length === 0) {
        if (contenedorListado) contenedorListado.innerHTML = '<p>No hay productos disponibles.</p>';
        if (contenedorDestacados) contenedorDestacados.innerHTML = '<p>No hay productos destacados.</p>';
        return;
      }

      const renderProducto = (prod) => {
        const div = document.createElement('div');
        div.classList.add('producto');
        div.innerHTML = `
          <img src="${prod.imagen_url || 'img/placeholder.png'}" alt="${prod.nombre}" />
          <h3>${prod.nombre}</h3>
          <p>${prod.descripcion}</p>
          <p><strong>Precio:</strong> $${prod.precio.toFixed(2)}</p>
          <p><strong>Stock:</strong> ${prod.stock}</p>
          <button class="btn-agregar">Agregar al carrito</button>
        `;

        div.querySelector('.btn-agregar').addEventListener('click', () => {
          const productoParaCarrito = {
            id: prod.id,
            nombre: prod.nombre,
            precio: prod.precio,
          };
          window.agregarProductoAlCarrito(productoParaCarrito);
        });

        return div;
      };

      if (contenedorListado) {
        contenedorListado.innerHTML = ''; 
        data.forEach(prod => {
          contenedorListado.appendChild(renderProducto(prod));
        });
      }

    
      if (contenedorDestacados) {
        contenedorDestacados.innerHTML = '';
        const destacados = data.slice(0, 3);
        destacados.forEach(prod => {
          contenedorDestacados.appendChild(renderProducto(prod));
        });
      }
    })
    .catch(err => {
      if (contenedorListado) contenedorListado.innerHTML = '<p style="color:red;">Error al cargar productos.</p>';
      if (contenedorDestacados) contenedorDestacados.innerHTML = '<p style="color:red;">Error al cargar destacados.</p>';
      console.error(err);
    });

});
