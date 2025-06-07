"""
سكريبت لإنشاء نقطة نهاية مؤقتة لإعادة تعيين كلمة مرور المسؤول
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from src.models.user import User
from src.models.db import db

# إنشاء blueprint للإدارة
admin_reset = Blueprint('admin_reset', __name__, url_prefix='/admin_reset')

# مفتاح الأمان للتحقق - يجب تغييره في الإنتاج
SECURITY_KEY = "aljeel_hadith_secure_key_2025"

@admin_reset.route('/create_admin', methods=['POST'])
def create_admin():
    """إنشاء مستخدم مسؤول جديد أو إعادة تعيين كلمة المرور"""
    # التحقق من مفتاح الأمان
    security_key = request.form.get('security_key')
    if security_key != SECURITY_KEY:
        return jsonify({"status": "error", "message": "مفتاح الأمان غير صحيح"}), 403
    
    # بيانات المستخدم المسؤول
    username = request.form.get('username', 'admin')
    password = request.form.get('password', 'Admin123')
    full_name = request.form.get('full_name', 'مدير النظام')
    
    # البحث عن المستخدم المسؤول
    admin = User.query.filter_by(username=username).first()
    
    if admin:
        # إعادة تعيين كلمة المرور
        admin.password_hash = generate_password_hash(password)
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "تم إعادة تعيين كلمة مرور المستخدم المسؤول بنجاح",
            "username": username,
            "password": password
        })
    else:
        # إنشاء مستخدم مسؤول جديد
        admin = User(
            username=username,
            password=password,
            full_name=full_name,
            email='admin@example.com',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "تم إنشاء مستخدم مسؤول جديد بنجاح",
            "username": username,
            "password": password
        })

# دالة لتسجيل البلوبرنت في التطبيق
def register_admin_reset_blueprint(app):
    app.register_blueprint(admin_reset)
