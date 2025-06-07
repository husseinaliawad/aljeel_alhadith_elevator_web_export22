"""
مسارات إدارة قطع الغيار لتطبيق aljeel alhadith elevator
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.part import Part
from src.models.part_usage import PartUsage
from src.routes.auth import login_required, admin_required
from src.models.db import db
from datetime import datetime

# إنشاء blueprint لقطع الغيار
parts = Blueprint('parts', __name__, url_prefix='/parts')

# عرض قائمة قطع الغيار
@parts.route('/')
@login_required
def index():
    # الحصول على معلمة التصفية من الاستعلام
    category_filter = request.args.get('category', 'all')
    stock_filter = request.args.get('stock', 'all')
    
    # بناء الاستعلام الأساسي
    query = Part.query
    
    # تطبيق التصفية حسب الفئة
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    # تطبيق التصفية حسب المخزون
    if stock_filter == 'low':
        query = query.filter(Part.quantity < Part.min_quantity)
    elif stock_filter == 'out':
        query = query.filter(Part.quantity == 0)
    
    # تنفيذ الاستعلام
    parts_list = query.order_by(Part.name).all()
    
    # الحصول على قائمة الفئات المتاحة
    categories = db.session.query(Part.category).distinct().all()
    categories = [category[0] for category in categories if category[0]]
    
    return render_template('parts/index.html', 
                          parts=parts_list, 
                          categories=categories,
                          category_filter=category_filter,
                          stock_filter=stock_filter)

# إضافة قطعة غيار جديدة
@parts.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        part_number = request.form.get('part_number')
        description = request.form.get('description')
        category = request.form.get('category')
        quantity = request.form.get('quantity', 0)
        min_quantity = request.form.get('min_quantity', 0)
        price = request.form.get('price', 0.0)
        supplier = request.form.get('supplier')
        
        new_part = Part(
            name=name,
            part_number=part_number,
            description=description,
            category=category,
            quantity=int(quantity),
            min_quantity=int(min_quantity),
            price=float(price),
            supplier=supplier
        )
        
        db.session.add(new_part)
        db.session.commit()
        
        flash('تم إضافة قطعة الغيار بنجاح', 'success')
        return redirect(url_for('parts.index'))
    
    # الحصول على قائمة الفئات المتاحة للاختيار
    categories = db.session.query(Part.category).distinct().all()
    categories = [category[0] for category in categories if category[0]]
    
    return render_template('parts/add.html', categories=categories)

# عرض تفاصيل قطعة غيار
@parts.route('/<int:part_id>')
@login_required
def view(part_id):
    part = Part.query.get_or_404(part_id)
    
    # الحصول على سجل استخدام قطعة الغيار
    part_usages = PartUsage.query.filter_by(part_id=part_id).order_by(PartUsage.usage_date.desc()).all()
    
    # تجميع معلومات الاستخدام
    usage_history = []
    for usage in part_usages:
        from src.models.maintenance_request import MaintenanceRequest
        request = MaintenanceRequest.query.get(usage.request_id)
        if request:
            usage_history.append({
                'usage_id': usage.id,
                'request_id': usage.request_id,
                'building_name': request.building_name,
                'quantity_used': usage.quantity_used,
                'usage_date': usage.usage_date
            })
    
    return render_template('parts/view.html', 
                          part=part,
                          usage_history=usage_history)

# تعديل قطعة غيار
@parts.route('/edit/<int:part_id>', methods=['GET', 'POST'])
@login_required
def edit(part_id):
    part = Part.query.get_or_404(part_id)
    
    if request.method == 'POST':
        part.name = request.form.get('name')
        part.part_number = request.form.get('part_number')
        part.description = request.form.get('description')
        part.category = request.form.get('category')
        part.quantity = int(request.form.get('quantity', 0))
        part.min_quantity = int(request.form.get('min_quantity', 0))
        part.price = float(request.form.get('price', 0.0))
        part.supplier = request.form.get('supplier')
        
        db.session.commit()
        
        flash('تم تحديث قطعة الغيار بنجاح', 'success')
        return redirect(url_for('parts.view', part_id=part.id))
    
    # الحصول على قائمة الفئات المتاحة للاختيار
    categories = db.session.query(Part.category).distinct().all()
    categories = [category[0] for category in categories if category[0]]
    
    return render_template('parts/edit.html', 
                          part=part,
                          categories=categories)

# حذف قطعة غيار
@parts.route('/delete/<int:part_id>', methods=['POST'])
@login_required
def delete(part_id):
    part = Part.query.get_or_404(part_id)
    
    # التحقق من عدم وجود استخدامات لقطعة الغيار
    usages = PartUsage.query.filter_by(part_id=part_id).count()
    if usages > 0:
        flash('لا يمكن حذف قطعة الغيار لوجود استخدامات مرتبطة بها', 'danger')
        return redirect(url_for('parts.view', part_id=part.id))
    
    db.session.delete(part)
    db.session.commit()
    
    flash('تم حذف قطعة الغيار بنجاح', 'success')
    return redirect(url_for('parts.index'))

# تعديل كمية قطعة الغيار
@parts.route('/adjust_quantity/<int:part_id>', methods=['GET', 'POST'])
@login_required
def adjust_quantity(part_id):
    part = Part.query.get_or_404(part_id)
    
    if request.method == 'POST':
        adjustment_type = request.form.get('adjustment_type')
        quantity = int(request.form.get('quantity', 0))
        reason = request.form.get('reason')
        
        if adjustment_type == 'add':
            part.quantity += quantity
            action = 'إضافة'
        else:  # remove
            if quantity > part.quantity:
                flash('الكمية المطلوب خصمها أكبر من الكمية المتوفرة', 'danger')
                return render_template('parts/adjust_quantity.html', part=part)
            
            part.quantity -= quantity
            action = 'خصم'
        
        db.session.commit()
        
        flash(f'تم {action} الكمية بنجاح', 'success')
        return redirect(url_for('parts.view', part_id=part.id))
    
    return render_template('parts/adjust_quantity.html', part=part)

# تقرير المخزون
@parts.route('/inventory_report')
@login_required
def inventory_report():
    # الحصول على جميع قطع الغيار
    parts_list = Part.query.all()
    
    # حساب إجمالي قيمة المخزون
    total_value = sum(part.quantity * part.price for part in parts_list)
    
    # حساب عدد قطع الغيار منخفضة المخزون
    low_stock_count = Part.query.filter(Part.quantity < Part.min_quantity).count()
    
    # حساب عدد قطع الغيار غير المتوفرة
    out_of_stock_count = Part.query.filter(Part.quantity == 0).count()
    
    return render_template('parts/inventory_report.html',
                          parts=parts_list,
                          total_value=total_value,
                          low_stock_count=low_stock_count,
                          out_of_stock_count=out_of_stock_count)

# واجهة برمجة التطبيقات لقطع الغيار
@parts.route('/api/list')
@login_required
def api_list():
    category_filter = request.args.get('category', 'all')
    stock_filter = request.args.get('stock', 'all')
    
    query = Part.query
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    if stock_filter == 'low':
        query = query.filter(Part.quantity < Part.min_quantity)
    elif stock_filter == 'out':
        query = query.filter(Part.quantity == 0)
    
    parts_list = query.order_by(Part.name).all()
    
    return jsonify([part.to_dict() for part in parts_list])

# واجهة برمجة التطبيقات لتفاصيل قطعة غيار
@parts.route('/api/<int:part_id>')
@login_required
def api_view(part_id):
    part = Part.query.get_or_404(part_id)
    return jsonify(part.to_dict())
