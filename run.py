#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Starting Supermarket Management System...")

try:
    print("Loading application...")
    from app import app, db
    print("Application loaded successfully!")

    # Initialize database
    print("Initializing database...")
    with app.app_context():
        db.create_all()
        print("Database initialized!")

    print("Starting server on port 5000...")
    print("=" * 50)
    print("Open browser and go to: http://localhost:5000")
    print("Username: admin")
    print("Password: admin123")
    print("=" * 50)
    print("Press Ctrl+C to stop server")
    print()

    app.run(host='127.0.0.1', port=5000, debug=True)
    
except ImportError as e:
    print(f"❌ خطأ في استيراد التطبيق: {e}")
    print("تأكد من تثبيت جميع المتطلبات: pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ خطأ في تشغيل التطبيق: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    input("\nاضغط Enter للخروج...")
