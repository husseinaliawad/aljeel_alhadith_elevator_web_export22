"""
مسارات المستخدمين لتطبيق aljeel alhadith elevator
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.user import User
from src.models.db import db
from datetime import datetime
from functools import wraps

# إنشاء blueprint للمستخدمين
auth = Blueprint('auth', __name__)

# دالة للتحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# دالة للتحقق من صلاحيات المدير
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'admin':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# صفحة تسجيل الدخول
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('هذا الحساب غير نشط. يرجى التواصل مع المدير', 'danger')
                return render_template('auth/login.html')
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            # تحديث آخر تسجيل دخول
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'مرحباً بك {user.full_name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('auth/login.html')

# تسجيل الخروج
@auth.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('auth.login'))

# إدارة المستخدمين (للمدير فقط)
@auth.route('/users')
@admin_required
def users():
    users_list = User.query.all()
    return render_template('auth/users.html', users=users_list)

# إضافة مستخدم جديد
@auth.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        
        # التحقق من عدم وجود مستخدم بنفس اسم المستخدم
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('اسم المستخدم موجود بالفعل', 'danger')
            return render_template('auth/add_user.html')
        
        new_user = User(
            username=username,
            password=password,
            full_name=full_name,
            email=email,
            phone=phone,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/add_user.html')

# تعديل مستخدم
@auth.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.role = request.form.get('role')
        user.is_active = 'is_active' in request.form
        
        # تحديث كلمة المرور إذا تم إدخالها
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        
        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/edit_user.html', user=user)

# حذف مستخدم
@auth.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # لا يمكن حذف المستخدم الحالي
    if user.id == session.get('user_id'):
        flash('لا يمكنك حذف حسابك الحالي', 'danger')
        return redirect(url_for('auth.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('auth.users'))

# الملف الشخصي للمستخدم
@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        
        # تحديث كلمة المرور إذا تم إدخالها
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if current_password and new_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                flash('تم تحديث كلمة المرور بنجاح', 'success')
            else:
                flash('كلمة المرور الحالية غير صحيحة', 'danger')
                return render_template('auth/profile.html', user=user)
        
        db.session.commit()
        
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', user=user)

# واجهة برمجة التطبيقات للمستخدمين
@auth.route('/api/users', methods=['GET'])
@login_required
def api_users():
    users_list = User.query.all()
    return jsonify([user.to_dict() for user in users_list])
