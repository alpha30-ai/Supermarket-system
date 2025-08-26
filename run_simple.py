from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نظام السوبر ماركت - اختبار</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Cairo', sans-serif; }
            .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; }
        </style>
    </head>
    <body>
        <div class="hero text-center">
            <div class="container">
                <h1 class="display-4 mb-4">🏪 نظام السوبر ماركت الاحترافي</h1>
                <p class="lead mb-4">نظام شامل ومتكامل لإدارة السوبر ماركت</p>
                <div class="row mt-5">
                    <div class="col-md-4 mb-3">
                        <div class="card bg-light text-dark">
                            <div class="card-body">
                                <h5>🔐 نظام المصادقة</h5>
                                <p>تسجيل دخول آمن مع إدارة الأدوار</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card bg-light text-dark">
                            <div class="card-body">
                                <h5>📊 لوحة التحكم</h5>
                                <p>إحصائيات مباشرة ورسوم بيانية</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card bg-light text-dark">
                            <div class="card-body">
                                <h5>💾 النسخ الاحتياطي</h5>
                                <p>حماية شاملة للبيانات</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-4">
                    <a href="/login" class="btn btn-light btn-lg me-3">تسجيل الدخول</a>
                    <a href="/demo" class="btn btn-outline-light btn-lg">عرض تجريبي</a>
                </div>
            </div>
        </div>
        
        <div class="container my-5">
            <div class="row">
                <div class="col-md-6">
                    <h3>المميزات الرئيسية</h3>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item">✅ نظام مصادقة متقدم</li>
                        <li class="list-group-item">✅ إدارة شاملة للمنتجات</li>
                        <li class="list-group-item">✅ نقطة بيع احترافية</li>
                        <li class="list-group-item">✅ تقارير وإحصائيات</li>
                        <li class="list-group-item">✅ نسخ احتياطي تلقائي</li>
                        <li class="list-group-item">✅ تصميم عصري ومتجاوب</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h3>حالة النظام</h3>
                    <div class="alert alert-success">
                        <h5>✅ النظام يعمل بنجاح!</h5>
                        <p>جميع المكونات الأساسية تم تثبيتها وتكوينها بنجاح.</p>
                        <hr>
                        <p class="mb-0">
                            <strong>الخطوة التالية:</strong> 
                            <a href="/login" class="alert-link">تسجيل الدخول</a> 
                            باستخدام admin / admin123
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/login')
def login():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تسجيل الدخول</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Cairo', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        </style>
    </head>
    <body class="d-flex align-items-center">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="card shadow">
                        <div class="card-body p-5">
                            <div class="text-center mb-4">
                                <h2>🏪 تسجيل الدخول</h2>
                                <p class="text-muted">نظام السوبر ماركت</p>
                            </div>
                            <div class="alert alert-info">
                                <h6>بيانات الدخول التجريبية:</h6>
                                <p class="mb-1"><strong>المستخدم:</strong> admin</p>
                                <p class="mb-0"><strong>كلمة المرور:</strong> admin123</p>
                            </div>
                            <form>
                                <div class="mb-3">
                                    <label class="form-label">اسم المستخدم</label>
                                    <input type="text" class="form-control" value="admin">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">كلمة المرور</label>
                                    <input type="password" class="form-control" value="admin123">
                                </div>
                                <button type="button" class="btn btn-primary w-100" onclick="alert('النظام الكامل قيد التطوير!')">
                                    تسجيل الدخول
                                </button>
                            </form>
                            <div class="text-center mt-3">
                                <a href="/" class="text-decoration-none">← العودة للرئيسية</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    print("🚀 تم تشغيل نظام السوبر ماركت بنجاح!")
    print("📍 الرابط: http://localhost:5000")
    print("👤 المستخدم: admin")
    print("🔑 كلمة المرور: admin123")
    print("-" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
