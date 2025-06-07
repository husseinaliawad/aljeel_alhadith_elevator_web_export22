"""
مسارات إدارة المستندات لتطبيق الجيل الحديث للأمن والمصاعد
"""

import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from src.models.db import db
from src.models.document import Document, DocumentCategory, Tag, DocumentPermission, DocumentEntityLink, DocumentVersion
from src.routes.auth import admin_required

# إنشاء blueprint لمسارات إدارة المستندات
documents = Blueprint('documents', __name__, url_prefix='/documents')

# التحقق من امتدادات الملفات المسموح بها
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """التحقق من أن امتداد الملف مسموح به"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    """إنشاء اسم فريد للملف"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename

@documents.route('/', methods=['GET'])
@login_required
def index():
    """عرض قائمة المستندات"""
    # الحصول على معايير التصفية
    category_id = request.args.get('category_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    search_query = request.args.get('q', '')
    
    # استعلام قاعدة البيانات
    query = Document.query
    
    # تطبيق معايير التصفية
    if category_id:
        query = query.join(Document.categories).filter(DocumentCategory.id == category_id)
    
    if tag_id:
        query = query.join(Document.tags).filter(Tag.id == tag_id)
    
    if search_query:
        query = query.filter(
            (Document.title.ilike(f'%{search_query}%')) | 
            (Document.description.ilike(f'%{search_query}%'))
        )
    
    # الحصول على المستندات
    documents_list = query.order_by(Document.upload_date.desc()).all()
    
    # الحصول على التصنيفات والوسوم
    categories = DocumentCategory.query.all()
    tags = Tag.query.all()
    
    return render_template(
        'documents/index.html',
        documents=documents_list,
        categories=categories,
        tags=tags,
        selected_category_id=category_id,
        selected_tag_id=tag_id,
        search_query=search_query
    )

@documents.route('/<int:document_id>', methods=['GET'])
@login_required
def view_document(document_id):
    """عرض تفاصيل مستند محدد"""
    document = Document.query.get_or_404(document_id)
    
    # التحقق من صلاحيات المستخدم
    if not current_user.is_admin:
        permission = DocumentPermission.query.filter_by(
            document_id=document_id,
            user_id=current_user.id,
            permission_type='read'
        ).first()
        
        if not permission:
            flash('ليس لديك صلاحية لعرض هذا المستند', 'danger')
            return redirect(url_for('documents.index'))
    
    # الحصول على الإصدارات
    versions = DocumentVersion.query.filter_by(document_id=document_id).order_by(DocumentVersion.version_number.desc()).all()
    
    # الحصول على الكيانات المرتبطة
    entity_links = DocumentEntityLink.query.filter_by(document_id=document_id).all()
    
    # الحصول على الصلاحيات
    permissions = DocumentPermission.query.filter_by(document_id=document_id).all()
    
    return render_template(
        'documents/view.html',
        document=document,
        versions=versions,
        entity_links=entity_links,
        permissions=permissions
    )

@documents.route('/add', methods=['GET', 'POST'])
@login_required
def add_document():
    """إضافة مستند جديد"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_ids = request.form.getlist('category_ids')
        tag_names = request.form.get('tags', '').split(',')
        
        # التحقق من البيانات
        if not title:
            flash('يرجى إدخال عنوان المستند', 'danger')
            return redirect(url_for('documents.add_document'))
        
        # التحقق من الملف
        if 'file' not in request.files:
            flash('يرجى اختيار ملف', 'danger')
            return redirect(url_for('documents.add_document'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(url_for('documents.add_document'))
        
        if not allowed_file(file.filename):
            flash('نوع الملف غير مسموح به', 'danger')
            return redirect(url_for('documents.add_document'))
        
        try:
            # حفظ الملف
            filename = secure_filename(file.filename)
            unique_filename = get_unique_filename(filename)
            
            # إنشاء مجلد المستندات إذا لم يكن موجوداً
            documents_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
            if not os.path.exists(documents_dir):
                os.makedirs(documents_dir)
            
            file_path = os.path.join(documents_dir, unique_filename)
            file.save(file_path)
            
            # إنشاء المستند
            document = Document(
                title=title,
                description=description,
                file_path=os.path.join('documents', unique_filename),
                file_type=filename.rsplit('.', 1)[1].lower() if '.' in filename else '',
                file_size=os.path.getsize(file_path),
                user_id=current_user.id
            )
            
            # إضافة التصنيفات
            if category_ids:
                categories = DocumentCategory.query.filter(DocumentCategory.id.in_(category_ids)).all()
                document.categories = categories
            
            # إضافة الوسوم
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    document.tags.append(tag)
            
            db.session.add(document)
            db.session.commit()
            
            flash('تم إضافة المستند بنجاح', 'success')
            return redirect(url_for('documents.view_document', document_id=document.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة المستند: {str(e)}', 'danger')
    
    # الحصول على التصنيفات
    categories = DocumentCategory.query.all()
    
    return render_template(
        'documents/add.html',
        categories=categories
    )

@documents.route('/<int:document_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(document_id):
    """تعديل مستند"""
    document = Document.query.get_or_404(document_id)
    
    # التحقق من صلاحيات المستخدم
    if not current_user.is_admin:
        permission = DocumentPermission.query.filter_by(
            document_id=document_id,
            user_id=current_user.id,
            permission_type='write'
        ).first()
        
        if not permission and document.user_id != current_user.id:
            flash('ليس لديك صلاحية لتعديل هذا المستند', 'danger')
            return redirect(url_for('documents.view_document', document_id=document_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_ids = request.form.getlist('category_ids')
        tag_names = request.form.get('tags', '').split(',')
        
        # التحقق من البيانات
        if not title:
            flash('يرجى إدخال عنوان المستند', 'danger')
            return redirect(url_for('documents.edit_document', document_id=document_id))
        
        try:
            # تحديث بيانات المستند
            document.title = title
            document.description = description
            
            # تحديث التصنيفات
            if category_ids:
                categories = DocumentCategory.query.filter(DocumentCategory.id.in_(category_ids)).all()
                document.categories = categories
            else:
                document.categories = []
            
            # تحديث الوسوم
            document.tags = []
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    document.tags.append(tag)
            
            # التحقق من الملف
            if 'file' in request.files and request.files['file'].filename != '':
                file = request.files['file']
                
                if not allowed_file(file.filename):
                    flash('نوع الملف غير مسموح به', 'danger')
                    return redirect(url_for('documents.edit_document', document_id=document_id))
                
                # حفظ الإصدار السابق
                old_version = DocumentVersion(
                    document_id=document.id,
                    version_number=document.version,
                    file_path=document.file_path,
                    file_size=document.file_size,
                    user_id=current_user.id
                )
                db.session.add(old_version)
                
                # حفظ الملف الجديد
                filename = secure_filename(file.filename)
                unique_filename = get_unique_filename(filename)
                
                documents_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
                if not os.path.exists(documents_dir):
                    os.makedirs(documents_dir)
                
                file_path = os.path.join(documents_dir, unique_filename)
                file.save(file_path)
                
                # تحديث بيانات الملف
                document.file_path = os.path.join('documents', unique_filename)
                document.file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                document.file_size = os.path.getsize(file_path)
                document.version += 1
            
            document.last_modified = datetime.utcnow()
            db.session.commit()
            
            flash('تم تعديل المستند بنجاح', 'success')
            return redirect(url_for('documents.view_document', document_id=document.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تعديل المستند: {str(e)}', 'danger')
    
    # الحصول على التصنيفات
    categories = DocumentCategory.query.all()
    
    # تحضير الوسوم
    tags = ', '.join([tag.name for tag in document.tags])
    
    return render_template(
        'documents/edit.html',
        document=document,
        categories=categories,
        tags=tags
    )

@documents.route('/<int:document_id>/delete', methods=['POST'])
@login_required
def delete_document(document_id):
    """حذف مستند"""
    document = Document.query.get_or_404(document_id)
    
    # التحقق من صلاحيات المستخدم
    if not current_user.is_admin:
        permission = DocumentPermission.query.filter_by(
            document_id=document_id,
            user_id=current_user.id,
            permission_type='delete'
        ).first()
        
        if not permission and document.user_id != current_user.id:
            flash('ليس لديك صلاحية لحذف هذا المستند', 'danger')
            return redirect(url_for('documents.view_document', document_id=document_id))
    
    try:
        # حذف الملف
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # حذف الإصدارات
        for version in document.versions:
            version_path = os.path.join(current_app.config['UPLOAD_FOLDER'], version.file_path)
            if os.path.exists(version_path):
                os.remove(version_path)
        
        # حذف المستند من قاعدة البيانات
        db.session.delete(document)
        db.session.commit()
        
        flash('تم حذف المستند بنجاح', 'success')
        return redirect(url_for('documents.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المستند: {str(e)}', 'danger')
        return redirect(url_for('documents.view_document', document_id=document_id))

@documents.route('/download/<int:document_id>', methods=['GET'])
@login_required
def download_document(document_id):
    """تحميل المستند"""
    document = Document.query.get_or_404(document_id)
    
    # التحقق من صلاحيات المستخدم
    if not current_user.is_admin:
        permission = DocumentPermission.query.filter_by(
            document_id=document_id,
            user_id=current_user.id,
            permission_type='read'
        ).first()
        
        if not permission and document.user_id != current_user.id:
            flash('ليس لديك صلاحية لتحميل هذا المستند', 'danger')
            return redirect(url_for('documents.index'))
    
    # الحصول على مسار الملف
    file_path = document.file_path
    directory = os.path.dirname(os.path.join(current_app.config['UPLOAD_FOLDER'], file_path))
    filename = os.path.basename(file_path)
    
    return send_from_directory(
        directory,
        filename,
        as_attachment=True,
        download_name=f"{document.title}.{document.file_type}"
    )

@documents.route('/categories', methods=['GET'])
@login_required
def categories():
    """عرض قائمة التصنيفات"""
    categories_list = DocumentCategory.query.all()
    return render_template('documents/categories.html', categories=categories_list)

@documents.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """إضافة تصنيف جديد"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        
        if not name:
            flash('يرجى إدخال اسم التصنيف', 'danger')
            return redirect(url_for('documents.add_category'))
        
        try:
            category = DocumentCategory(
                name=name,
                description=description,
                parent_id=parent_id if parent_id else None
            )
            
            db.session.add(category)
            db.session.commit()
            
            flash('تم إضافة التصنيف بنجاح', 'success')
            return redirect(url_for('documents.categories'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة التصنيف: {str(e)}', 'danger')
    
    # الحصول على التصنيفات الأب
    parent_categories = DocumentCategory.query.all()
    
    return render_template(
        'documents/add_category.html',
        parent_categories=parent_categories
    )

@documents.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """تعديل تصنيف"""
    category = DocumentCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        
        if not name:
            flash('يرجى إدخال اسم التصنيف', 'danger')
            return redirect(url_for('documents.edit_category', category_id=category_id))
        
        try:
            category.name = name
            category.description = description
            category.parent_id = parent_id if parent_id and int(parent_id) != category_id else None
            
            db.session.commit()
            
            flash('تم تعديل التصنيف بنجاح', 'success')
            return redirect(url_for('documents.categories'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تعديل التصنيف: {str(e)}', 'danger')
    
    # الحصول على التصنيفات الأب
    parent_categories = DocumentCategory.query.filter(DocumentCategory.id != category_id).all()
    
    return render_template(
        'documents/edit_category.html',
        category=category,
        parent_categories=parent_categories
    )

@documents.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """حذف تصنيف"""
    category = DocumentCategory.query.get_or_404(category_id)
    
    try:
        # التحقق من وجود تصنيفات فرعية
        if category.children:
            flash('لا يمكن حذف التصنيف لأنه يحتوي على تصنيفات فرعية', 'danger')
            return redirect(url_for('documents.categories'))
        
        # حذف التصنيف
        db.session.delete(category)
        db.session.commit()
        
        flash('تم حذف التصنيف بنجاح', 'success')
        return redirect(url_for('documents.categories'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف التصنيف: {str(e)}', 'danger')
        return redirect(url_for('documents.categories'))

@documents.route('/tags', methods=['GET'])
@login_required
def tags():
    """عرض قائمة الوسوم"""
    tags_list = Tag.query.all()
    return render_template('documents/tags.html', tags=tags_list)

@documents.route('/search', methods=['GET'])
@login_required
def search():
    """البحث المتقدم في المستندات"""
    # الحصول على معايير البحث
    query = request.args.get('q', '')
    category_ids = request.args.getlist('category_ids')
    tag_ids = request.args.getlist('tag_ids')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id', type=int)
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id', type=int)
    
    # استعلام قاعدة البيانات
    documents_query = Document.query
    
    # تطبيق معايير البحث
    if query:
        documents_query = documents_query.filter(
            (Document.title.ilike(f'%{query}%')) | 
            (Document.description.ilike(f'%{query}%'))
        )
    
    if category_ids:
        documents_query = documents_query.join(Document.categories).filter(DocumentCategory.id.in_(category_ids))
    
    if tag_ids:
        documents_query = documents_query.join(Document.tags).filter(Tag.id.in_(tag_ids))
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            documents_query = documents_query.filter(Document.upload_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            documents_query = documents_query.filter(Document.upload_date <= end_date_obj)
        except ValueError:
            pass
    
    if user_id:
        documents_query = documents_query.filter(Document.user_id == user_id)
    
    if entity_type and entity_id:
        documents_query = documents_query.join(Document.entity_links).filter(
            (DocumentEntityLink.entity_type == entity_type) & 
            (DocumentEntityLink.entity_id == entity_id)
        )
    
    # الحصول على المستندات
    documents_list = documents_query.order_by(Document.upload_date.desc()).all()
    
    # الحصول على التصنيفات والوسوم والمستخدمين
    categories = DocumentCategory.query.all()
    tags_list = Tag.query.all()
    users = User.query.all()
    
    return render_template(
        'documents/search.html',
        documents=documents_list,
        categories=categories,
        tags=tags_list,
        users=users,
        query=query,
        selected_category_ids=category_ids,
        selected_tag_ids=tag_ids,
        start_date=start_date,
        end_date=end_date,
        selected_user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id
    )

@documents.route('/<int:document_id>/permissions', methods=['GET'])
@login_required
@admin_required
def document_permissions(document_id):
    """عرض صلاحيات المستند"""
    document = Document.query.get_or_404(document_id)
    permissions = DocumentPermission.query.filter_by(document_id=document_id).all()
    users = User.query.all()
    
    return render_template(
        'documents/permissions.html',
        document=document,
        permissions=permissions,
        users=users
    )

@documents.route('/<int:document_id>/permissions/add', methods=['POST'])
@login_required
@admin_required
def add_permission(document_id):
    """إضافة صلاحية جديدة"""
    document = Document.query.get_or_404(document_id)
    
    user_id = request.form.get('user_id', type=int)
    permission_type = request.form.get('permission_type')
    
    if not user_id or not permission_type:
        flash('يرجى اختيار المستخدم ونوع الصلاحية', 'danger')
        return redirect(url_for('documents.document_permissions', document_id=document_id))
    
    try:
        # التحقق من وجود الصلاحية مسبقاً
        existing_permission = DocumentPermission.query.filter_by(
            document_id=document_id,
            user_id=user_id,
            permission_type=permission_type
        ).first()
        
        if existing_permission:
            flash('الصلاحية موجودة مسبقاً', 'warning')
            return redirect(url_for('documents.document_permissions', document_id=document_id))
        
        # إضافة الصلاحية
        permission = DocumentPermission(
            document_id=document_id,
            user_id=user_id,
            permission_type=permission_type
        )
        
        db.session.add(permission)
        db.session.commit()
        
        flash('تم إضافة الصلاحية بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إضافة الصلاحية: {str(e)}', 'danger')
    
    return redirect(url_for('documents.document_permissions', document_id=document_id))

@documents.route('/<int:document_id>/permissions/<int:permission_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_permission(document_id, permission_id):
    """حذف صلاحية"""
    permission = DocumentPermission.query.get_or_404(permission_id)
    
    # التحقق من أن الصلاحية تنتمي للمستند المحدد
    if permission.document_id != document_id:
        flash('الصلاحية غير موجودة', 'danger')
        return redirect(url_for('documents.document_permissions', document_id=document_id))
    
    try:
        db.session.delete(permission)
        db.session.commit()
        
        flash('تم حذف الصلاحية بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الصلاحية: {str(e)}', 'danger')
    
    return redirect(url_for('documents.document_permissions', document_id=document_id))

@documents.route('/<int:document_id>/link-entity', methods=['POST'])
@login_required
def link_entity(document_id):
    """ربط المستند بكيان آخر"""
    document = Document.query.get_or_404(document_id)
    
    entity_type = request.form.get('entity_type')
    entity_id = request.form.get('entity_id', type=int)
    
    if not entity_type or not entity_id:
        flash('يرجى اختيار نوع الكيان ومعرفه', 'danger')
        return redirect(url_for('documents.view_document', document_id=document_id))
    
    try:
        # التحقق من وجود الربط مسبقاً
        existing_link = DocumentEntityLink.query.filter_by(
            document_id=document_id,
            entity_type=entity_type,
            entity_id=entity_id
        ).first()
        
        if existing_link:
            flash('الربط موجود مسبقاً', 'warning')
            return redirect(url_for('documents.view_document', document_id=document_id))
        
        # إضافة الربط
        link = DocumentEntityLink(
            document_id=document_id,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        db.session.add(link)
        db.session.commit()
        
        flash('تم ربط المستند بالكيان بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء ربط المستند: {str(e)}', 'danger')
    
    return redirect(url_for('documents.view_document', document_id=document_id))

@documents.route('/<int:document_id>/unlink-entity/<int:link_id>', methods=['POST'])
@login_required
def unlink_entity(document_id, link_id):
    """إلغاء ربط المستند بكيان"""
    link = DocumentEntityLink.query.get_or_404(link_id)
    
    # التحقق من أن الربط ينتمي للمستند المحدد
    if link.document_id != document_id:
        flash('الربط غير موجود', 'danger')
        return redirect(url_for('documents.view_document', document_id=document_id))
    
    try:
        db.session.delete(link)
        db.session.commit()
        
        flash('تم إلغاء ربط المستند بالكيان بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إلغاء ربط المستند: {str(e)}', 'danger')
    
    return redirect(url_for('documents.view_document', document_id=document_id))
