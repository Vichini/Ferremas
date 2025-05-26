from app import app, db, Usuario, Producto
from werkzeug.security import generate_password_hash

with app.app_context():
    # Crear tablas si no existen
    db.create_all()

    # Crear usuarios iniciales
    usuarios_iniciales = [
        Usuario(
            nombre='Admin Ferremas',
            correo='admin@ferremas.com',
            password=generate_password_hash('admin123'),
            rol='admin'
        ),
        Usuario(
            nombre='Vendedor 1',
            correo='vendedor@ferremas.com',
            password=generate_password_hash('vendedor123'),
            rol='vendedor'
        ),
        Usuario(
            nombre='Cliente Ejemplo',
            correo='cliente@ferremas.com',
            password=generate_password_hash('cliente123'),
            rol='cliente'
        ),
    ]

    # Insertar usuarios si no existen
    for u in usuarios_iniciales:
        if not Usuario.query.filter_by(correo=u.correo).first():
            db.session.add(u)

    # Crear productos iniciales
    productos_iniciales = [
        Producto(
            nombre='Martillo',
            descripcion='Martillo de acero de alta resistencia',
            precio=15000,
            stock=20
        ),
        Producto(
            nombre='Taladro eléctrico',
            descripcion='Taladro inalámbrico con batería recargable',
            precio=45000,
            stock=10
        ),
        Producto(
            nombre='Destornillador múltiple',
            descripcion='Set de destornilladores con varias puntas',
            precio=12000,
            stock=30
        ),
    ]

    # Insertar productos si no existen
    for p in productos_iniciales:
        if not Producto.query.filter_by(nombre=p.nombre).first():
            db.session.add(p)

    db.session.commit()
    print("Datos iniciales insertados correctamente.")
