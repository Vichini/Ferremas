from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # Habilitar CORS solo para React

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ferremas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# Decorador de autenticación con rol
def requiere_rol(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = request.authorization
            if not auth:
                return jsonify({"mensaje": "Autenticación requerida"}), 401
            usuario = Usuario.query.filter_by(correo=auth.username).first()
            if not usuario or not check_password_hash(usuario.password, auth.password):
                return jsonify({"mensaje": "Credenciales inválidas"}), 401
            if usuario.rol not in roles_permitidos:
                return jsonify({"mensaje": "No tiene permiso para esta acción"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    return jsonify({"mensaje": "API FERREMAS en funcionamiento"})

# Registro y login
@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
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
    usuario = Usuario.query.filter_by(correo=datos['correo']).first()
    if not usuario:
        return jsonify({"mensaje": "Correo no registrado"}), 404
    if check_password_hash(usuario.password, datos['password']):
        return jsonify({
            "mensaje": f"Bienvenido, {usuario.nombre}",
            "rol": usuario.rol
        }), 200
    else:
        return jsonify({"mensaje": "Contraseña incorrecta"}), 401

# CRUD Productos
@app.route('/productos', methods=['POST'])
@requiere_rol('admin', 'vendedor')
def crear_producto():
    datos = request.get_json()
    nuevo_producto = Producto(
        nombre=datos['nombre'],
        descripcion=datos.get('descripcion', ''),
        precio=datos['precio'],
        stock=datos['stock']
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify({"mensaje": "Producto creado correctamente"}), 201

@app.route('/productos', methods=['GET'])
def listar_productos():
    productos = Producto.query.all()
    return jsonify([{
        "id": p.id,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "precio": p.precio,
        "stock": p.stock
    } for p in productos])

@app.route('/productos/<int:id>', methods=['PUT'])
@requiere_rol('admin', 'vendedor')
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)
    datos = request.get_json()
    producto.nombre = datos.get('nombre', producto.nombre)
    producto.descripcion = datos.get('descripcion', producto.descripcion)
    producto.precio = datos.get('precio', producto.precio)
    producto.stock = datos.get('stock', producto.stock)
    db.session.commit()
    return jsonify({"mensaje": "Producto actualizado correctamente"})

@app.route('/productos/<int:id>', methods=['DELETE'])
@requiere_rol('admin', 'vendedor')
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({"mensaje": "Producto eliminado correctamente"})

# Gestión Pedidos Clientes
@app.route('/pedidos', methods=['POST'])
@requiere_rol('cliente')
def crear_pedido():
    datos = request.get_json()
    usuario = Usuario.query.filter_by(correo=request.authorization.username).first()
    productos_pedido = datos.get('productos')
    if not productos_pedido:
        return jsonify({"mensaje": "Debe enviar al menos un producto en el pedido"}), 400
    total = 0
    detalles = []
    for item in productos_pedido:
        producto = Producto.query.get(item['producto_id'])
        if not producto:
            return jsonify({"mensaje": f"Producto ID {item['producto_id']} no encontrado"}), 404
        if producto.stock < item['cantidad']:
            return jsonify({"mensaje": f"Stock insuficiente para producto {producto.nombre}"}), 400
        subtotal = producto.precio * item['cantidad']
        total += subtotal
        detalles.append((producto, item['cantidad'], subtotal))
    nuevo_pedido = Pedido(usuario_id=usuario.id, total=total)
    db.session.add(nuevo_pedido)
    db.session.flush()
    for producto, cantidad, subtotal in detalles:
        detalle = DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=producto.id,
            cantidad=cantidad,
            subtotal=subtotal
        )
        producto.stock -= cantidad
        db.session.add(detalle)
    db.session.commit()
    return jsonify({"mensaje": "Pedido creado correctamente", "pedido_id": nuevo_pedido.id}), 201

@app.route('/mis_pedidos', methods=['GET'])
@requiere_rol('cliente')
def listar_mis_pedidos():
    usuario = Usuario.query.filter_by(correo=request.authorization.username).first()
    pedidos = Pedido.query.filter_by(usuario_id=usuario.id).all()
    resultado = []
    for pedido in pedidos:
        detalles = [{
            "producto": d.producto.nombre,
            "cantidad": d.cantidad,
            "subtotal": d.subtotal
        } for d in pedido.detalles]
        resultado.append({
            "pedido_id": pedido.id,
            "fecha": pedido.fecha.isoformat(),
            "total": pedido.total,
            "estado": pedido.estado,
            "detalles": detalles
        })
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
