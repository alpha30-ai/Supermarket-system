from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import shutil
import sqlite3
import bcrypt
from functools import wraps

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supermarket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد قاعدة البيانات
db = SQLAlchemy(app)

# إعداد نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# نماذج قاعدة البيانات
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='cashier')  # admin, manager, cashier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    avatar_url = db.Column(db.String(200), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=5)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    payment_method = db.Column(db.String(20), default='cash')  # cash, card, mixed
    cashier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('SaleItem', backref='sale', lazy=True)

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='sale_items')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    address = db.Column(db.Text, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    customer_type = db.Column(db.String(20), default='regular')  # regular, vip, premium
    loyalty_points = db.Column(db.Integer, default=0)
    total_purchases = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    sales = db.relationship('Sale', backref='customer', lazy=True)

# دالة للتحقق من الأدوار
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role and current_user.role != 'admin':
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# الصفحات الرئيسية
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            # تحديث آخر دخول
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # إحصائيات سريعة
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_products = Product.query.filter(Product.stock_quantity <= Product.min_stock).count()
    today_sales = Sale.query.filter(Sale.created_at >= datetime.now().date()).count()
    today_revenue = db.session.query(db.func.sum(Sale.total_amount)).filter(
        Sale.created_at >= datetime.now().date()).scalar() or 0
    
    return render_template('dashboard.html',
                         total_products=total_products,
                         low_stock_products=low_stock_products,
                         today_sales=today_sales,
                         today_revenue=today_revenue)

@app.route('/products')
@login_required
def products():
    # Get all products with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Build query with filters
    query = Product.query.filter_by(is_active=True)

    # Search filter
    search = request.args.get('search', '')
    if search:
        query = query.filter(Product.name.contains(search))

    # Category filter
    category_id = request.args.get('category', '')
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Stock filter
    stock_filter = request.args.get('stock', '')
    if stock_filter == 'in_stock':
        query = query.filter(Product.stock_quantity > Product.min_stock)
    elif stock_filter == 'low_stock':
        query = query.filter(Product.stock_quantity <= Product.min_stock)
        query = query.filter(Product.stock_quantity > 0)
    elif stock_filter == 'out_of_stock':
        query = query.filter(Product.stock_quantity == 0)

    products = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = Category.query.filter_by(is_active=True).all()

    return render_template('products.html',
                         products=products,
                         categories=categories,
                         search=search,
                         category_filter=category_id,
                         stock_filter=stock_filter)

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    try:
        # Get form data
        name = request.form.get('name')
        barcode = request.form.get('barcode')
        category_id = request.form.get('category_id')
        unit = request.form.get('unit', 'قطعة')
        cost_price = float(request.form.get('cost_price'))
        price = float(request.form.get('price'))
        stock_quantity = int(request.form.get('stock_quantity'))
        min_stock = int(request.form.get('min_stock', 5))
        description = request.form.get('description', '')

        # Create new product
        product = Product(
            name=name,
            barcode=barcode,
            category_id=category_id,
            unit=unit,
            cost_price=cost_price,
            price=price,
            stock_quantity=stock_quantity,
            min_stock=min_stock,
            description=description,
            is_active=True
        )

        db.session.add(product)
        db.session.commit()

        flash('تم إضافة المنتج بنجاح', 'success')
        return redirect(url_for('products'))

    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء إضافة المنتج', 'error')
        return redirect(url_for('products'))

@app.route('/pos')
@login_required
def pos():
    # Get all active products for POS
    products = Product.query.filter_by(is_active=True).filter(Product.stock_quantity > 0).all()
    categories = Category.query.filter_by(is_active=True).all()
    customers = Customer.query.filter_by(is_active=True).all()

    return render_template('pos.html',
                         products=products,
                         categories=categories,
                         customers=customers)

@app.route('/api/products/search')
@login_required
def search_products():
    query = request.args.get('q', '')
    category_id = request.args.get('category', '')

    # Build search query
    products_query = Product.query.filter_by(is_active=True).filter(Product.stock_quantity > 0)

    if query:
        products_query = products_query.filter(
            db.or_(
                Product.name.contains(query),
                Product.barcode.contains(query)
            )
        )

    if category_id:
        products_query = products_query.filter(Product.category_id == category_id)

    products = products_query.limit(20).all()

    # Convert to JSON
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'stock': product.stock_quantity,
            'image': product.image_path or '/static/images/default-product.svg',
            'barcode': product.barcode
        })

    return jsonify(products_data)

@app.route('/reports')
@login_required
def reports():

    # حساب التواريخ الافتراضية
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    # حساب الإحصائيات
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.min_stock,
        Product.stock_quantity > 0
    ).count()

    # أفضل المنتجات (محاكاة)
    top_products = Product.query.filter_by(is_active=True).limit(5).all()
    for product in top_products:
        product.sold_quantity = 50  # محاكاة
        product.revenue = product.price * 50

    # منتجات قليلة المخزون
    low_stock_items = Product.query.filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.min_stock
    ).limit(10).all()

    return render_template('reports.html',
                         start_date=start_date,
                         end_date=end_date,
                         total_revenue=45750.00,  # محاكاة
                         total_sales=150,  # محاكاة
                         total_products=total_products,
                         low_stock_products=low_stock_products,
                         top_products=top_products,
                         low_stock_items=low_stock_items)

@app.route('/users')
@login_required
def users():
    # التحقق من صلاحيات المدير
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('dashboard'))

    # الحصول على معاملات البحث والفلترة
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')

    # بناء الاستعلام
    query = User.query

    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )

    if role_filter:
        query = query.filter(User.role == role_filter)

    if status_filter:
        is_active = status_filter == 'active'
        query = query.filter(User.is_active == is_active)

    # ترتيب وترقيم
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    # حساب الإحصائيات
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(role='admin').count()
    cashier_users = User.query.filter_by(role='cashier').count()

    return render_template('users.html',
                         users=users,
                         total_users=total_users,
                         active_users=active_users,
                         admin_users=admin_users,
                         cashier_users=cashier_users)

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    # التحقق من صلاحيات المدير
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية لإضافة مستخدمين', 'error')
        return redirect(url_for('users'))

    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == '1'

        # التحقق من صحة البيانات
        if not username or not password or not role:
            flash('جميع الحقول المطلوبة يجب ملؤها', 'error')
            return redirect(url_for('users'))

        if password != confirm_password:
            flash('كلمة المرور وتأكيدها غير متطابقتين', 'error')
            return redirect(url_for('users'))

        # التحقق من عدم وجود المستخدم
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود بالفعل', 'error')
            return redirect(url_for('users'))

        if email and User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني موجود بالفعل', 'error')
            return redirect(url_for('users'))

        # إنشاء المستخدم الجديد
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password.decode('utf-8'),
            role=role,
            is_active=is_active
        )

        db.session.add(new_user)
        db.session.commit()

        flash(f'تم إضافة المستخدم {username} بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء إضافة المستخدم', 'error')

    return redirect(url_for('users'))

@app.route('/backup')
@login_required
def backup():
    # التحقق من صلاحيات المدير
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('dashboard'))

    # محاكاة بيانات النسخ الاحتياطية
    backups = [
        {
            'filename': 'backup_2024_01_15_14_30.zip',
            'created_at': datetime.now() - timedelta(days=1),
            'file_size': '2.5 MB',
            'backup_type': 'auto',
            'status': 'completed'
        },
        {
            'filename': 'backup_2024_01_14_09_15.zip',
            'created_at': datetime.now() - timedelta(days=2),
            'file_size': '2.3 MB',
            'backup_type': 'manual',
            'status': 'completed'
        }
    ]

    return render_template('backup.html',
                         backups=backups,
                         total_backups=len(backups),
                         last_backup_date='2024-01-15 14:30',
                         database_size='2.1 MB',
                         auto_backup_status='مفعل',
                         backup_frequency='24',
                         storage_used='4.8 MB',
                         auto_backup_enabled=True,
                         max_backups=10)

@app.route('/api/backup/create', methods=['POST'])
@login_required
def create_backup():
    # التحقق من صلاحيات المدير
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية'})

    try:
        # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # إنشاء اسم الملف
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M')
        backup_filename = f'backup_{timestamp}.zip'
        backup_path = os.path.join(backup_dir, backup_filename)

        # نسخ قاعدة البيانات
        db_path = os.path.join(os.path.dirname(__file__), 'supermarket.db')

        import zipfile
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            if os.path.exists(db_path):
                zipf.write(db_path, 'supermarket.db')

            # إضافة ملفات أخرى إذا لزم الأمر
            static_dir = os.path.join(os.path.dirname(__file__), 'static')
            if os.path.exists(static_dir):
                for root, dirs, files in os.walk(static_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(__file__))
                        zipf.write(file_path, arcname)

        return jsonify({
            'success': True,
            'message': 'تم إنشاء النسخة الاحتياطية بنجاح',
            'filename': backup_filename
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'فشل في إنشاء النسخة الاحتياطية: {str(e)}'
        })

@app.route('/customers')
@login_required
def customers():
    # الحصول على معاملات البحث والفلترة
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')

    # بناء الاستعلام
    query = Customer.query

    if search:
        query = query.filter(
            db.or_(
                Customer.name.contains(search),
                Customer.phone.contains(search),
                Customer.email.contains(search)
            )
        )

    if type_filter:
        query = query.filter(Customer.customer_type == type_filter)

    if status_filter:
        is_active = status_filter == 'active'
        query = query.filter(Customer.is_active == is_active)

    # ترتيب وترقيم
    customers = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    # حساب الإحصائيات
    total_customers = Customer.query.count()
    vip_customers = Customer.query.filter_by(customer_type='vip').count()

    # حساب متوسط المشتريات
    avg_purchases = db.session.query(db.func.avg(Customer.total_purchases)).scalar() or 0

    # حساب إجمالي النقاط
    total_points = db.session.query(db.func.sum(Customer.loyalty_points)).scalar() or 0

    # حساب العملاء الجدد هذا الشهر
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_customers_this_month = Customer.query.filter(Customer.created_at >= start_of_month).count()

    return render_template('customers.html',
                         customers=customers,
                         total_customers=total_customers,
                         vip_customers=vip_customers,
                         avg_purchases=f"{avg_purchases:.2f}",
                         total_points=total_points,
                         new_customers_this_month=new_customers_this_month)

@app.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        birth_date = request.form.get('birth_date')
        customer_type = request.form.get('customer_type', 'regular')
        loyalty_points = int(request.form.get('loyalty_points', 0))

        # التحقق من صحة البيانات
        if not name or not phone:
            flash('الاسم ورقم الهاتف مطلوبان', 'error')
            return redirect(url_for('customers'))

        # التحقق من عدم وجود العميل
        if Customer.query.filter_by(phone=phone).first():
            flash('رقم الهاتف موجود بالفعل', 'error')
            return redirect(url_for('customers'))

        if email and Customer.query.filter_by(email=email).first():
            flash('البريد الإلكتروني موجود بالفعل', 'error')
            return redirect(url_for('customers'))

        # تحويل تاريخ الميلاد
        birth_date_obj = None
        if birth_date:
            try:
                birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                pass

        # إنشاء العميل الجديد
        new_customer = Customer(
            name=name,
            phone=phone,
            email=email if email else None,
            address=address,
            birth_date=birth_date_obj,
            customer_type=customer_type,
            loyalty_points=loyalty_points
        )

        db.session.add(new_customer)
        db.session.commit()

        flash(f'تم إضافة العميل {name} بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء إضافة العميل', 'error')

    return redirect(url_for('customers'))

# API لإتمام عملية البيع
@app.route('/api/pos/complete_sale', methods=['POST'])
@login_required
def complete_sale():
    try:
        data = request.get_json()
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'cash')
        customer_id = data.get('customer_id')

        if not items:
            return jsonify({'success': False, 'message': 'لا توجد منتجات في السلة'})

        # حساب المجموع
        total_amount = 0
        sale_items = []

        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({'success': False, 'message': f'المنتج غير موجود: {item["name"]}'})

            if product.stock_quantity < item['quantity']:
                return jsonify({'success': False, 'message': f'المخزون غير كافي للمنتج: {product.name}'})

            item_total = product.price * item['quantity']
            total_amount += item_total

            sale_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': product.price,
                'total': item_total
            })

        # إنشاء عملية البيع
        sale = Sale(
            total_amount=total_amount,
            payment_method=payment_method,
            cashier_id=current_user.id,
            customer_id=customer_id if customer_id else None
        )
        db.session.add(sale)
        db.session.flush()  # للحصول على ID

        # إضافة عناصر البيع وتحديث المخزون
        for item in sale_items:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['price'],
                total=item['total']
            )
            db.session.add(sale_item)

            # تحديث المخزون
            item['product'].stock_quantity -= item['quantity']

        # تحديث نقاط العميل إذا كان موجود
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer:
                # إضافة نقاط (1 نقطة لكل 10 جنيه)
                points_earned = int(total_amount / 10)
                customer.loyalty_points += points_earned
                customer.total_purchases += total_amount

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'تم إتمام عملية البيع بنجاح',
            'sale_id': sale.id,
            'total': total_amount
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إتمام البيع'})

# صفحة الملف الشخصي
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# تحديث الملف الشخصي
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        # تحديث البيانات الأساسية
        current_user.email = request.form.get('email', current_user.email)

        # تحديث كلمة المرور إذا تم إدخالها
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('كلمة المرور الحالية غير صحيحة', 'error')
                return redirect(url_for('profile'))

            if new_password != confirm_password:
                flash('كلمة المرور الجديدة وتأكيدها غير متطابقين', 'error')
                return redirect(url_for('profile'))

            if len(new_password) < 6:
                flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'error')
                return redirect(url_for('profile'))

            current_user.set_password(new_password)
            flash('تم تحديث كلمة المرور بنجاح', 'success')

        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح', 'success')

    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء تحديث الملف الشخصي', 'error')

    return redirect(url_for('profile'))

if __name__ == '__main__':
    print("🚀 بدء تشغيل نظام إدارة السوبر ماركت...")
    with app.app_context():
        db.create_all()
        
        # إنشاء مستخدم افتراضي إذا لم يكن موجوداً
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@supermarket.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("تم إنشاء المستخدم الافتراضي: admin / admin123")

        # إنشاء عملاء تجريبيين
        if Customer.query.count() == 0:
            customers_data = [
                {
                    'name': 'أحمد محمد علي',
                    'phone': '01234567890',
                    'email': 'ahmed@example.com',
                    'customer_type': 'vip',
                    'loyalty_points': 150,
                    'total_purchases': 2500.00
                },
                {
                    'name': 'فاطمة حسن',
                    'phone': '01098765432',
                    'email': 'fatma@example.com',
                    'customer_type': 'premium',
                    'loyalty_points': 200,
                    'total_purchases': 3200.00
                },
                {
                    'name': 'محمد عبدالله',
                    'phone': '01555123456',
                    'customer_type': 'regular',
                    'loyalty_points': 50,
                    'total_purchases': 800.00
                },
                {
                    'name': 'سارة أحمد',
                    'phone': '01777888999',
                    'email': 'sara@example.com',
                    'customer_type': 'vip',
                    'loyalty_points': 300,
                    'total_purchases': 4500.00
                }
            ]

            for customer_data in customers_data:
                customer = Customer(**customer_data)
                db.session.add(customer)

            db.session.commit()
            print("تم إنشاء العملاء التجريبيين")

        # إنشاء فئات افتراضية
        if not Category.query.first():
            categories = [
                Category(name='مواد غذائية', description='المواد الغذائية الأساسية', is_active=True),
                Category(name='مشروبات', description='المشروبات والعصائر', is_active=True),
                Category(name='منظفات', description='مواد التنظيف والصابون', is_active=True),
                Category(name='أدوات شخصية', description='أدوات العناية الشخصية', is_active=True),
                Category(name='منتجات الألبان', description='الحليب والجبن واللبن', is_active=True)
            ]
            for category in categories:
                db.session.add(category)
            db.session.commit()
            print("تم إنشاء الفئات الافتراضية")
    
    print("🌐 تشغيل الخادم...")
    print("=" * 50)
    print("🔗 الرابط: http://localhost:5000")
    print("👤 اسم المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
