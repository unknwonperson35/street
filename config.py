import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey123'

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'streetbasket.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    VENDOR_DOCS_FOLDER = os.path.join(UPLOAD_FOLDER, 'vendor_docs')
    SUPPLIER_DOCS_FOLDER = os.path.join(UPLOAD_FOLDER, 'supplier_docs')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
