#  Ferremas - Sistema de Ferretería

---

## 🚀 Descripción

Ferremas es un sistema web para gestión de productos, usuarios y ventas para una ferretería.  
Implementa funcionalidades de carrito de compras, autenticación JWT, integración con Transbank para pagos y manejo de stock de productos.

---

## 🛠 Tecnologías usadas

| Tecnología    | Descripción                            |
| ------------- | ------------------------------------ |
| 🔥 Flask      | Framework backend en Python           |
| 🐍 SQLAlchemy | ORM para base de datos SQLite         |
| 💳 Transbank  | Integración de pagos Webpay Plus (TEST) |
| 💻 Frontend   | HTML, CSS y JavaScript puro           |
| 🔐 JWT        | Autenticación basada en tokens        |

---

## 📁 Estructura principal

```plaintext
backend/
├── app.py                   # Aplicación Flask y rutas principales
├── transbank_routes.py      # Rutas para integración con Transbank
├── models.py                # Modelos de la base de datos
├── migrations/              # Migraciones de base de datos
├── instance/                # Configuración privada
├── init_db.py               # Script para inicializar DB y datos
├── requirements.txt         # Dependencias del proyecto
venv/                        # Entorno virtual Python
frontend/
├── index.html               # Página principal
├── login.html               # Página de login
├── productos.html           # Listado de productos
├── carrito.html             # Carrito de compras
├── js/                     # Scripts JS
└── css/                    # Estilos CSS

⚙️ Instalación y configuración
Clonar repositorio

bash
Copiar
Editar
git clone https://github.com/tu_usuario/ferremas.git
cd ferremas/backend
Crear y activar entorno virtual

bash
Copiar
Editar
python -m venv venv
source venv/bin/activate   # Linux/macOS
# o
venv\Scripts\activate      # Windows
Instalar dependencias

bash
Copiar
Editar
pip install -r requirements.txt
Inicializar base de datos y datos iniciales

bash
Copiar
Editar
python init_db.py
Migraciones (para futuros cambios)

bash
Copiar
Editar
flask db init       # Solo la primera vez
flask db migrate -m "Mensaje de migración"
flask db upgrade
▶️ Ejecución
Backend
bash
Copiar
Editar
export FLASK_APP=app.py       # Linux/macOS
set FLASK_APP=app.py          # Windows

flask run
Servidor correrá en http://127.0.0.1:5000/

Frontend
Abre la carpeta frontend/ con VSCode.

Haz click derecho en index.html y selecciona Open with Live Server.

El frontend se servirá localmente y podrá comunicarse con el backend.

📝 Uso

Visita index.html para ver página principal.

Usa usuario ejemplo para login:

Cliente: juan@example.com / 123456

Explora productos, agrégalos al carrito y finaliza compra.

Se crea un pedido y se inicia el pago con Transbank (modo TEST).

Administra stock y productos desde el backend vía API.
----------------------------------------------------------------
🔗 Rutas principales API
Ruta	Método	Descripción
/login	POST	Autenticación, devuelve JWT
/productos	GET	Listar productos
/pedido	POST	Crear pedido (requiere token)
/transbank/iniciar_pago	POST	Inicia pago Webpay
/producto/sumar_stock	POST	Sumar stock a un producto

⚠️ Notas importantes-----------------------------------------------------
Transbank en modo TEST, no para producción.

Ajusta URLs backend si cambias servidores o puertos.

JWT almacenado en localStorage.

Datos iniciales no se duplican en reinicios.

Frontend y backend están desacoplados, se comunican con fetch.

¿Quieres ayuda para desplegar en producción o integrar más funciones?
¡Pregunta sin compromiso! 😄

© 2025 Ferremas - Todos los derechos reservados.
