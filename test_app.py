#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# إضافة المجلد الحالي إلى مسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("بدء تشغيل التطبيق...")
    from app import app, db
    
    print("إنشاء قاعدة البيانات...")
    with app.app_context():
        db.create_all()
        print("تم إنشاء قاعدة البيانات بنجاح")
    
    print("تشغيل الخادم...")
    print("الرابط: http://localhost:5000")
    print("اسم المستخدم: admin")
    print("كلمة المرور: admin123")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"خطأ في تشغيل التطبيق: {e}")
    import traceback
    traceback.print_exc()
    input("اضغط Enter للخروج...")
