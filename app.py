import os
import re
from flask import Flask, render_template, request, redirect, flash, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import Markup
from functools import wraps

# === Flask App Setup ===
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streetbasket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['VENDOR_DOCS_FOLDER'] = 'uploads/vendor_docs'
app.config['SUPPLIER_DOCS_FOLDER'] = 'uploads/supplier_docs'
app.config['PRODUCT_IMAGE_FOLDER'] = 'static/uploads'

# Create folders if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VENDOR_DOCS_FOLDER'], exist_ok=True)
os.makedirs(app.config['SUPPLIER_DOCS_FOLDER'], exist_ok=True)
os.makedirs(app.config['PRODUCT_IMAGE_FOLDER'], exist_ok=True)

# Allowed extensions
ALLOWED_DOC_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_doc_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# Initialize DB
db = SQLAlchemy(app)

# === Models ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200))
    location = db.Column(db.String(200))
    role = db.Column(db.String(20))  # 'vendor' or 'supplier'
    document = db.Column(db.String(200))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')

# === Filters ===
@app.template_filter('highlight_search')
def highlight_search(text, search):
    if not text or not search:
        return text
    pattern = re.compile(re.escape(search), re.IGNORECASE)
    highlighted = pattern.sub(lambda m: f'<mark class="bg-yellow-300">{m.group(0)}</mark>', text)
    return Markup(highlighted)

# === Auth Decorator ===
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'vendor_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('vendor_login'))
        return f(*args, **kwargs)
    return decorated_function

# === Routes ===
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/vendor-register', methods=['GET', 'POST'])
def vendor_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if Vendor.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(request.url)
        if Vendor.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(request.url)

        vendor = Vendor(username=username, email=email)
        vendor.set_password(password)
        db.session.add(vendor)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('vendor_login'))

    return render_template('vendor_register.html')

@app.route('/vendor-login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        vendor = Vendor.query.filter_by(username=username).first()

        if vendor and vendor.check_password(password):
            session['vendor_id'] = vendor.id
            session['vendor_username'] = vendor.username
            flash('Login successful!', 'success')
            return redirect(url_for('vendor_dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(request.url)

    return render_template('vendor_login.html')

@app.route('/vendor-logout')
def vendor_logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('vendor_login'))

@app.route('/product-upload', methods=['GET', 'POST'])
@login_required
def product_upload():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        stock = request.form.get('stock')
        image = request.files.get('image')

        if not product_name or not price or not stock:
            flash("Please fill all required fields.", "error")
            return redirect(request.url)

        filename = None
        if image and allowed_image_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['PRODUCT_IMAGE_FOLDER'], filename))
        elif image:
            flash("Invalid image format.", "error")
            return redirect(request.url)

        vendor_id = session['vendor_id']
        new_product = Product(
            vendor_id=vendor_id,
            name=product_name,
            price=float(price),
            stock=int(stock),
            image_filename=filename
        )
        db.session.add(new_product)
        db.session.commit()

        flash(f"Product '{product_name}' uploaded successfully!", "success")
        return redirect(url_for('vendor_dashboard'))

    return render_template('product_upload.html')

@app.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.vendor_id != session['vendor_id']:
        abort(403)

    if request.method == 'POST':
        product.name = request.form.get('product_name')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))

        image = request.files.get('image')
        if image and allowed_image_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['PRODUCT_IMAGE_FOLDER'], filename))
            product.image_filename = filename

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('vendor_dashboard'))

    return render_template('edit_product.html', product=product)

@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.vendor_id != session['vendor_id']:
        abort(403)

    if product.image_filename:
        try:
            os.remove(os.path.join(app.config['PRODUCT_IMAGE_FOLDER'], product.image_filename))
        except Exception as e:
            print('Error deleting image:', e)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('vendor_dashboard'))

@app.route('/vendor-dashboard')
@login_required
def vendor_dashboard():
    vendor_id = session['vendor_id']
    page = request.args.get('page', 1, type=int)
    per_page = 6

    search_query = request.args.get('search', '')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    stock_filter = request.args.get('stock_filter', '')

    query = Product.query.filter_by(vendor_id=vendor_id)

    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)
    if stock_filter == 'in_stock':
        query = query.filter(Product.stock > 0)
    elif stock_filter == 'out_of_stock':
        query = query.filter(Product.stock <= 0)

    pagination = query.paginate(page=page, per_page=per_page)
    products = pagination.items

    return render_template('vendor_dashboard.html', products=products, pagination=pagination,
                           search_query=search_query, price_min=price_min,
                           price_max=price_max, stock_filter=stock_filter)

@app.route('/upload_product', methods=['GET', 'POST'])
def upload_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            product = Product(name=name, price=price, image_filename=filename)
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('upload_product.html')

# === Run App ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
