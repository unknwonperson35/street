from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -------------------- Vendor Model --------------------
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(150))
    doc_filename = db.Column(db.String(200))  # Uploaded documents

    orders = db.relationship('Order', backref='vendor', lazy=True)


# -------------------- Supplier Model --------------------
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(150))
    doc_filename = db.Column(db.String(200))  # Uploaded documents

    products = db.relationship('Product', backref='supplier', lazy=True)


# -------------------- Product Model --------------------
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20))  # e.g., kg, litre
    price_per_unit = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(100))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)

    orders = db.relationship('Order', backref='product', lazy=True)


# -------------------- Order Model --------------------
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pending')  # Pending / Approved / Delivered
    order_date = db.Column(db.DateTime, server_default=db.func.now())


# -------------------- DB Initializer --------------------
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
