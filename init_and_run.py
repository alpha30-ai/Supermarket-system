#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Initializing Supermarket Management System...")

try:
    # Import the app and database
    from app import app, db, User, Category, Customer
    
    print("Creating database tables...")
    
    # Create application context and initialize database
    with app.app_context():
        # Drop all tables first (clean slate)
        db.drop_all()
        print("Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("Created all database tables")
        
        # Create default admin user
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@supermarket.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin user: admin / admin123")
        
        # Create default categories
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
            print("Created default categories")

            # Create sample products
            from app import Product
            sample_products = [
                # مواد غذائية
                Product(name='أرز أبيض 1 كيلو', barcode='1234567890123', price=15.50, cost_price=12.00, stock_quantity=100, min_stock=10, category_id=1, is_active=True),
                Product(name='سكر أبيض 1 كيلو', barcode='1234567890124', price=12.00, cost_price=9.50, stock_quantity=80, min_stock=15, category_id=1, is_active=True),
                Product(name='زيت طبخ 1 لتر', barcode='1234567890125', price=25.00, cost_price=20.00, stock_quantity=50, min_stock=10, category_id=1, is_active=True),
                Product(name='معكرونة 500 جرام', barcode='1234567890126', price=8.50, cost_price=6.00, stock_quantity=120, min_stock=20, category_id=1, is_active=True),

                # مشروبات
                Product(name='كوكا كولا 330 مل', barcode='1234567890127', price=3.50, cost_price=2.50, stock_quantity=200, min_stock=50, category_id=2, is_active=True),
                Product(name='عصير برتقال 1 لتر', barcode='1234567890128', price=12.00, cost_price=9.00, stock_quantity=60, min_stock=15, category_id=2, is_active=True),
                Product(name='مياه معدنية 1.5 لتر', barcode='1234567890129', price=2.00, cost_price=1.20, stock_quantity=300, min_stock=100, category_id=2, is_active=True),

                # منظفات
                Product(name='صابون غسيل 1 كيلو', barcode='1234567890130', price=18.00, cost_price=14.00, stock_quantity=40, min_stock=10, category_id=3, is_active=True),
                Product(name='شامبو 400 مل', barcode='1234567890131', price=35.00, cost_price=28.00, stock_quantity=30, min_stock=8, category_id=4, is_active=True),

                # منتجات الألبان
                Product(name='حليب طازج 1 لتر', barcode='1234567890132', price=8.00, cost_price=6.50, stock_quantity=90, min_stock=20, category_id=5, is_active=True),
                Product(name='جبنة بيضاء 250 جرام', barcode='1234567890133', price=22.00, cost_price=18.00, stock_quantity=45, min_stock=12, category_id=5, is_active=True),
            ]

            for product in sample_products:
                db.session.add(product)
            db.session.commit()
            print("Created sample products")
        
        # Create sample customers
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
            print("Created sample customers")
    
    print("Database initialization completed successfully!")
    print("=" * 50)
    print("Starting Flask server...")
    print("URL: http://127.0.0.1:5000")
    print("Username: admin")
    print("Password: admin123")
    print("=" * 50)
    
    # Start the Flask application
    app.run(host='127.0.0.1', port=5000, debug=True)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
