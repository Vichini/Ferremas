from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_migrate import Migrate
import jwt
import requests

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500"
], supports_credentials=True)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ferremas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tu_clave_secreta_muy_segura'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagen_url = db.Column(db.String(250))

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default='pendiente')
    usuario = db.relationship('Usuario', backref=db.backref('pedidos', lazy=True))

class DetallePedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    pedido = db.relationship('Pedido', backref=db.backref('detalles', lazy=True))
    producto = db.relationship('Producto')

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return jsonify({"mensaje": "API FERREMAS en funcionamiento"})

def token_requerido(roles_permitidos=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                partes = request.headers['Authorization'].split()
                if len(partes) == 2 and partes[0] == 'Bearer':
                    token = partes[1]
            if not token:
                return jsonify({'mensaje': 'Token de autenticación requerido'}), 401
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                usuario = Usuario.query.get(data['user_id'])
                if not usuario:
                    return jsonify({'mensaje': 'Usuario no encontrado'}), 401
                if roles_permitidos and usuario.rol not in roles_permitidos:
                    return jsonify({'mensaje': 'No tiene permiso para esta acción'}), 403
                return f(usuario, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({'mensaje': 'Token expirado'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'mensaje': 'Token inválido'}), 401
        return wrapper
    return decorator

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    if not datos:
        return jsonify({"mensaje": "Datos no proporcionados"}), 400
    required_fields = ['nombre', 'correo', 'password', 'rol']
    for campo in required_fields:
        if campo not in datos or not datos[campo]:
            return jsonify({"mensaje": f"El campo '{campo}' es obligatorio"}), 400
    if Usuario.query.filter_by(correo=datos['correo']).first():
        return jsonify({"mensaje": "Este correo ya está registrado"}), 400
    hashed_password = generate_password_hash(datos['password'])
    nuevo_usuario = Usuario(
        nombre=datos['nombre'],
        correo=datos['correo'],
        password=hashed_password,
        rol=datos['rol']
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario creado correctamente"}), 201

@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    if not datos or not datos.get('correo') or not datos.get('password'):
        return jsonify({"mensaje": "Correo y contraseña son requeridos"}), 400
    usuario = Usuario.query.filter_by(correo=datos['correo']).first()
    if not usuario:
        return jsonify({"mensaje": "Correo no registrado"}), 404
    if check_password_hash(usuario.password, datos['password']):
        token = jwt.encode({
            'user_id': usuario.id,
            'rol': usuario.rol,
            'exp': datetime.utcnow() + timedelta(hours=8)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            "mensaje": f"Bienvenido, {usuario.nombre}",
            "token": token,
            "rol": usuario.rol
        }), 200
    else:
        return jsonify({"mensaje": "Contraseña incorrecta"}), 401

@app.route('/usuario/me', methods=['GET'])
@token_requerido()
def obtener_perfil(usuario):
    return jsonify({
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol
    })

@app.route('/usuario/me', methods=['PUT'])
@token_requerido()
def actualizar_perfil(usuario):
    datos = request.get_json()
    if not datos:
        return jsonify({"mensaje": "Datos no proporcionados"}), 400
    if 'nombre' in datos:
        usuario.nombre = datos['nombre']
    if 'correo' in datos:
        if Usuario.query.filter(Usuario.correo == datos['correo'], Usuario.id != usuario.id).first():
            return jsonify({"mensaje": "Correo ya está en uso"}), 400
        usuario.correo = datos['correo']
    if 'password' in datos:
        usuario.password = generate_password_hash(datos['password'])
    db.session.commit()
    return jsonify({"mensaje": "Perfil actualizado correctamente"})

@app.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    lista_productos = []
    for p in productos:
        lista_productos.append({
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "precio": p.precio,
            "stock": p.stock,
            "imagen_url": p.imagen_url
        })
    return jsonify(lista_productos)

@app.route('/pedido', methods=['POST'])
@token_requerido()
def crear_pedido(usuario):
    datos = request.get_json()
    carrito = datos.get('carrito')
    if not carrito or not isinstance(carrito, list) or len(carrito) == 0:
        return jsonify({'mensaje': 'El carrito está vacío o inválido'}), 400

    total = 0
    detalles = []

    for item in carrito:
        producto = Producto.query.get(item.get('id'))
        if not producto:
            return jsonify({'mensaje': f'Producto con id {item.get("id")} no encontrado'}), 404
        cantidad = item.get('cantidad', 0)
        if cantidad <= 0:
            return jsonify({'mensaje': 'Cantidad inválida para algún producto'}), 400
        if producto.stock < cantidad:
            return jsonify({'mensaje': f'Stock insuficiente para el producto {producto.nombre}'}), 400

        subtotal = producto.precio * cantidad
        total += subtotal
        detalles.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })

    nuevo_pedido = Pedido(
        usuario_id=usuario.id,
        total=total,
        estado='pendiente'
    )
    db.session.add(nuevo_pedido)
    db.session.flush()

    for detalle in detalles:
        producto = detalle['producto']
        cantidad = detalle['cantidad']
        subtotal = detalle['subtotal']

        detalle_pedido = DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=producto.id,
            cantidad=cantidad,
            subtotal=subtotal
        )
        db.session.add(detalle_pedido)
        producto.stock -= cantidad

    db.session.commit()

    return jsonify({'mensaje': 'Pedido creado correctamente', 'pedido_id': nuevo_pedido.id}), 201
@app.route('/dolar', methods=['GET'])
def obtener_dolar():
    try:
        response = requests.get('https://mindicador.cl/api/dolar')
        if response.status_code != 200:
            return jsonify({"mensaje": "No se pudo obtener el valor del dólar"}), 500

        data = response.json()
        valor_dolar = data['serie'][0]['valor']
        return jsonify({"dolar": valor_dolar}), 200

    except Exception as e:
        return jsonify({"mensaje": "Error al obtener el dólar", "error": str(e)}), 500


from transbank_routes import transbank_bp
app.register_blueprint(transbank_bp)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
