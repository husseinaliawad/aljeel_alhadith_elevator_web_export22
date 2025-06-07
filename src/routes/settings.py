"""
مسارات إعدادات النظام لتطبيق الجيل الحديث للأمن والمصاعد
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from src.models.settings import SystemSettings
from src.routes.auth import login_required, admin_required
from src.models.db import db

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """التحقق من أن امتداد الملف مسموح به"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@settings_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    """عرض صفحة الإعدادات"""
    settings = SystemSettings.get_settings()
    return render_template('settings/index.html', settings=settings)

@settings_bp.route('/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """تحديث إعدادات النظام"""
    settings = SystemSettings.get_settings()
    
    # تحديث بيانات الشركة
    settings.update(
        company_name=request.form.get('company_name'),
        company_address=request.form.get('company_address'),
        company_phone=request.form.get('company_phone'),
        company_email=request.form.get('company_email'),
        company_website=request.form.get('company_website'),
        tax_number=request.form.get('tax_number'),
        commercial_register=request.form.get('commercial_register'),
        bank_account=request.form.get('bank_account'),
        bank_name=request.form.get('bank_name'),
        iban=request.form.get('iban')
    )
    
    flash('تم تحديث إعدادات النظام بنجاح', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/upload_logo', methods=['POST'])
@login_required
@admin_required
def upload_logo():
    """رفع شعار الشركة"""
    if 'logo' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('settings.index'))
    
    file = request.files['logo']
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('settings.index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # إنشاء اسم فريد للملف باستخدام الطابع الزمني
        import time
        unique_filename = f"logo_{int(time.time())}_{filename}"
        
        # التأكد من وجود المجلد
        upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # تحديث مسار الشعار في الإعدادات
        settings = SystemSettings.get_settings()
        relative_path = os.path.join('static', 'images', 'uploads', unique_filename)
        settings.update(logo_path=relative_path)
        
        flash('تم رفع شعار الشركة بنجاح', 'success')
    else:
        flash('صيغة الملف غير مسموح بها. الصيغ المسموحة هي: png, jpg, jpeg, gif', 'danger')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/upload_stamp', methods=['POST'])
@login_required
@admin_required
def upload_stamp():
    """رفع ختم الشركة"""
    if 'stamp' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('settings.index'))
    
    file = request.files['stamp']
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('settings.index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # إنشاء اسم فريد للملف باستخدام الطابع الزمني
        import time
        unique_filename = f"stamp_{int(time.time())}_{filename}"
        
        # التأكد من وجود المجلد
        upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # تحديث مسار الختم في الإعدادات
        settings = SystemSettings.get_settings()
        relative_path = os.path.join('static', 'images', 'uploads', unique_filename)
        settings.update(stamp_path=relative_path)
        
        flash('تم رفع ختم الشركة بنجاح', 'success')
    else:
        flash('صيغة الملف غير مسموح بها. الصيغ المسموحة هي: png, jpg, jpeg, gif', 'danger')
    
    return redirect(url_for('settings.index'))
