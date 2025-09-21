import os
import uuid
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
import click
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'app.db')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
UPLOAD_DIR = os.path.join(STATIC_DIR, 'uploads')
PICS_DIR = os.path.join(BASE_DIR, 'pics')
LOGOS_DIR = os.path.join(BASE_DIR, 'logos')
GOVT_UPLOAD_DIR = os.path.join(UPLOAD_DIR, 'govt_ids')
PRODUCT_UPLOAD_DIR = os.path.join(UPLOAD_DIR, 'products')

os.makedirs(GOVT_UPLOAD_DIR, exist_ok=True)
os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB file uploads
app.config['SECRET_KEY'] = app.config.get('SECRET_KEY') or 'dev-secret-change-me'

db = SQLAlchemy(app)

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    role = db.Column(db.String(20), nullable=False)  # 'buyer' | 'seller' | 'admin'
    password_hash = db.Column(db.LargeBinary(60), nullable=False)
    govt_id_path = db.Column(db.String(255))
    payment_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='seller', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_name = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(40))  # e.g., 'pots', 'wood', 'metal'
    status = db.Column(db.String(20), default='pending')  # 'pending' | 'approved' | 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt())


def check_password(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed)


def save_file(file_storage, dest_dir) -> str:
    filename = secure_filename(file_storage.filename or '')
    if not filename:
        raise ValueError('Invalid file')
    root, ext = os.path.splitext(filename)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(dest_dir, unique_name)
    file_storage.save(path)
    # Return web path relative to /static
    rel_path = os.path.relpath(path, STATIC_DIR)
    return f"/static/{rel_path.replace(os.sep, '/')}"


def get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='admin-auth')


def generate_admin_token(user_id: int) -> str:
    s = get_serializer()
    return s.dumps({'uid': user_id, 'role': 'admin'})


def verify_admin_token(token: str) -> int | None:
    s = get_serializer()
    try:
        data = s.loads(token, max_age=60 * 60 * 8)  # 8 hours
        if data.get('role') == 'admin' and 'uid' in data:
            return int(data['uid'])
        return None
    except (BadSignature, SignatureExpired):
        return None


# -----------------------------------------------------------------------------
# Lightweight migration helpers
# -----------------------------------------------------------------------------
def ensure_category_column():
    """Add 'category' column to products if it doesn't exist (SQLite only)."""
    from sqlalchemy import text
    with db.engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(products)"))
        cols = [row[1] for row in res.fetchall()]
        if 'category' not in cols:
            conn.execute(text("ALTER TABLE products ADD COLUMN category VARCHAR(40)"))
            conn.commit()


# -----------------------------------------------------------------------------
# DB init route (for convenience in dev)
# -----------------------------------------------------------------------------
@app.cli.command('init-db')
def init_db_cmd():
    db.create_all()
    ensure_category_column()
    print('Database initialized at', DB_PATH)


@app.cli.command('create-admin')
@click.option('--fullname', prompt=True)
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin_cmd(fullname, email, password):
    """Create an admin user (role=admin)."""
    with app.app_context():
        if User.query.filter_by(email=email).first():
            click.echo('User with this email already exists')
            return
        user = User(
            fullname=fullname,
            email=email,
            role='admin',
            password_hash=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin created: {email}')


# -----------------------------------------------------------------------------
# Auth routes
# -----------------------------------------------------------------------------
@app.post('/api/register/buyer')
def register_buyer():
    data = request.form
    required = ['fullname', 'email', 'phone', 'address', 'password']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'Missing field: {f}'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        fullname=data['fullname'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        role='buyer',
        password_hash=hash_password(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Buyer registered successfully'}), 201


@app.post('/api/register/seller')
def register_seller():
    data = request.form
    required = ['fullname', 'email', 'phone', 'address_location', 'payment_details', 'password']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'Missing field: {f}'}), 400

    if 'govt_id' not in request.files:
        return jsonify({'error': 'Government ID is required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    try:
        govt_path = save_file(request.files['govt_id'], GOVT_UPLOAD_DIR)
    except Exception as e:
        return jsonify({'error': f'Govt ID upload failed: {e}'}), 400

    user = User(
        fullname=data['fullname'],
        email=data['email'],
        phone=data['phone'],
        address=data['address_location'],
        role='seller',
        payment_details=data['payment_details'],
        password_hash=hash_password(data['password']),
        govt_id_path=govt_path,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Seller registered successfully'}), 201


@app.post('/api/login')
def login():
    data = request.form or request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  # optional; if provided must match

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401

    if role and role != user.role:
        return jsonify({'error': f'Please login as {user.role}'}), 403

    payload = {
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'fullname': user.fullname,
            'email': user.email,
            'role': user.role,
        }
    }
    if user.role == 'admin':
        payload['admin_token'] = generate_admin_token(user.id)
    return jsonify(payload), 200


# -----------------------------------------------------------------------------
# Product routes
# -----------------------------------------------------------------------------
@app.post('/api/products')
def create_product():
    data = request.form
    required = ['seller_email', 'seller_name', 'product_name', 'price', 'description', 'category']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'Missing field: {f}'}), 400

    user = User.query.filter_by(email=data['seller_email'], role='seller').first()
    if not user:
        return jsonify({'error': 'Seller not found'}), 404

    if 'product_image' not in request.files:
        return jsonify({'error': 'Product image is required'}), 400

    try:
        image_path = save_file(request.files['product_image'], PRODUCT_UPLOAD_DIR)
    except Exception as e:
        return jsonify({'error': f'Image upload failed: {e}'}), 400

    try:
        price = float(data['price'])
    except ValueError:
        return jsonify({'error': 'Invalid price'}), 400

    product = Product(
        seller_id=user.id,
        seller_name=data['seller_name'],
        name=data['product_name'],
        price=price,
        description=data['description'],
        image_path=image_path,
        category=data.get('category'),
        status='pending'
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'Product submitted for approval', 'id': product.id, 'status': product.status}), 201


@app.get('/api/products')
def list_products():
    status = request.args.get('status')
    category = request.args.get('category')
    query = Product.query
    if status in {'pending', 'approved', 'rejected'}:
        # If requesting anything other than approved, require admin token
        if status != 'approved':
            auth = request.headers.get('Authorization', '')
            token = auth.replace('Bearer ', '') if auth.startswith('Bearer ') else request.headers.get('X-Admin-Token')
            admin_id = verify_admin_token(token) if token else None
            if not admin_id:
                return jsonify({'error': 'Admin authorization required'}), 401
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    products = query.order_by(Product.created_at.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'seller_id': p.seller_id,
            'seller_name': p.seller_name,
            'name': p.name,
            'price': p.price,
            'description': p.description,
            'image_url': p.image_path,
            'category': p.category,
            'status': p.status,
            'created_at': p.created_at.isoformat()
        }
        for p in products
    ])


@app.get('/api/products/<int:product_id>')
def get_product(product_id: int):
    p = Product.query.get(product_id)
    if not p:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({
        'id': p.id,
        'seller_id': p.seller_id,
        'seller_name': p.seller_name,
        'name': p.name,
        'price': p.price,
        'description': p.description,
        'image_url': p.image_path,
        'category': p.category,
        'status': p.status,
        'created_at': p.created_at.isoformat()
    })


@app.patch('/api/products/<int:product_id>/status')
def update_product_status(product_id: int):
    # Require admin token
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '') if auth.startswith('Bearer ') else request.headers.get('X-Admin-Token')
    admin_id = verify_admin_token(token) if token else None
    if not admin_id:
        return jsonify({'error': 'Admin authorization required'}), 401

    data = request.get_json(silent=True) or {}
    new_status = data.get('status')
    if new_status not in {'pending', 'approved', 'rejected'}:
        return jsonify({'error': 'Invalid status'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    product.status = new_status
    db.session.commit()
    return jsonify({'message': 'Status updated', 'id': product.id, 'status': product.status})


@app.get('/api/my-products')
def my_products():
    seller_email = request.args.get('seller_email')
    if not seller_email:
        return jsonify({'error': 'seller_email is required'}), 400
    user = User.query.filter_by(email=seller_email, role='seller').first()
    if not user:
        return jsonify({'error': 'Seller not found'}), 404
    products = Product.query.filter_by(seller_id=user.id).order_by(Product.created_at.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'seller_id': p.seller_id,
            'seller_name': p.seller_name,
            'name': p.name,
            'price': p.price,
            'description': p.description,
            'image_url': p.image_path,
            'status': p.status,
            'created_at': p.created_at.isoformat()
        }
        for p in products
    ])


# -----------------------------------------------------------------------------
# Static files helper (optional convenience)
# -----------------------------------------------------------------------------
@app.get('/static/uploads/<path:filename>')
def uploaded_file(filename):
    # allow direct serving of uploaded files in dev
    return send_from_directory(UPLOAD_DIR, filename)


# -----------------------------------------------------------------------------
# Simple page routes (serve static HTML from templates/ via Flask)
# -----------------------------------------------------------------------------
@app.get('/')
def page_home():
    return send_from_directory(TEMPLATES_DIR, 'explore.html')


@app.get('/explore')
def page_explore():
    return send_from_directory(TEMPLATES_DIR, 'explore.html')


@app.get('/register')
def page_register():
    return send_from_directory(TEMPLATES_DIR, 'register.html')


@app.get('/login')
def page_login():
    return send_from_directory(TEMPLATES_DIR, 'login.html')


@app.get('/seller')
def page_seller():
    return send_from_directory(TEMPLATES_DIR, 'seller.html')


@app.get('/admin')
def page_admin():
    return send_from_directory(TEMPLATES_DIR, 'admin.html')


@app.get('/pots')
def page_pots():
    return send_from_directory(TEMPLATES_DIR, 'pots.html')


@app.get('/wood')
def page_wood():
    return send_from_directory(TEMPLATES_DIR, 'wood.html')


@app.get('/metal')
def page_metal():
    return send_from_directory(TEMPLATES_DIR, 'metal.html')


# -----------------------------------------------------------------------------
# Additional asset routes for legacy paths used in templates/CSS
# -----------------------------------------------------------------------------
@app.get('/pics/<path:filename>')
def serve_pics(filename):
    return send_from_directory(PICS_DIR, filename)


@app.get('/logos/<path:filename>')
def serve_logos(filename):
    return send_from_directory(LOGOS_DIR, filename)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_category_column()
    port = int(os.environ.get('PORT', 5002))
    app.run(host='127.0.0.1', port=port, debug=True)


