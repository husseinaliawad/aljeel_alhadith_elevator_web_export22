"""
مسارات إدارة طلبات الصيانة لتطبيق aljeel alhadith elevator
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.maintenance_request import MaintenanceRequest
from src.models.elevator import Elevator
from src.models.part import Part
from src.models.part_usage import PartUsage
from src.routes.auth import login_required
from src.models.db import db
from datetime import datetime

# إنشاء blueprint لطلبات الصيانة
requests = Blueprint('requests', __name__, url_prefix='/requests')

# عرض قائمة طلبات الصيانة
@requests.route('/')
@login_required
def index():
    # الحصول على معلمة التصفية من الاستعلام
    status_filter = request.args.get('status', 'all')
    
    # استعلام قاعدة البيانات بناءً على التصفية
    if status_filter == 'all':
        requests = MaintenanceRequest.query.order_by(MaintenanceRequest.request_date.desc()).all()
    else:
        requests = MaintenanceRequest.query.filter_by(status=status_filter).order_by(MaintenanceRequest.request_date.desc()).all()
    
    return render_template('requests/index.html', 
                          requests=requests, 
                          status_filter=status_filter)

# إضافة طلب صيانة جديد
@requests.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # الحصول على قائمة المصاعد للاختيار
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        elevator_id = request.form.get('elevator_id')
        issue_description = request.form.get('issue_description')
        priority = request.form.get('priority')
        
        # الحصول على معلومات المصعد
        elevator = Elevator.query.get(elevator_id)
        
        new_request = MaintenanceRequest(
            request_date=datetime.now().strftime('%Y-%m-%d'),
            building_name=elevator.building_name if elevator else "",
            elevator_id=elevator_id,
            issue_description=issue_description,
            priority=priority,
            status='جديد'
        )
        
        db.session.add(new_request)
        
        # تحديث حالة المصعد إلى "قيد الصيانة"
        if elevator:
            elevator.status = 'قيد الصيانة'
        
        db.session.commit()
        
        flash('تم إضافة طلب الصيانة بنجاح', 'success')
        return redirect(url_for('requests.index'))
    
    return render_template('requests/add.html', elevators=elevators)

# عرض تفاصيل طلب صيانة
@requests.route('/<int:request_id>')
@login_required
def view(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    
    # الحصول على المصعد المرتبط بالطلب
    elevator = Elevator.query.get(maintenance_request.elevator_id)
    
    # الحصول على قطع الغيار المستخدمة في هذا الطلب
    part_usages = PartUsage.query.filter_by(request_id=request_id).all()
    
    # تجميع معلومات قطع الغيار
    parts_info = []
    for usage in part_usages:
        part = Part.query.get(usage.part_id)
        if part:
            parts_info.append({
                'usage_id': usage.id,
                'part_id': part.id,
                'part_name': part.name,
                'quantity_used': usage.quantity_used,
                'usage_date': usage.usage_date
            })
    
    return render_template('requests/view.html', 
                          request=maintenance_request, 
                          elevator=elevator,
                          parts_info=parts_info)

# تعديل طلب صيانة
@requests.route('/edit/<int:request_id>', methods=['GET', 'POST'])
@login_required
def edit(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        elevator_id = request.form.get('elevator_id')
        issue_description = request.form.get('issue_description')
        priority = request.form.get('priority')
        status = request.form.get('status')
        
        # تحديث بيانات الطلب
        maintenance_request.elevator_id = elevator_id
        maintenance_request.issue_description = issue_description
        maintenance_request.priority = priority
        
        # إذا تم تغيير الحالة إلى "مكتمل"، قم بتعيين تاريخ الإكمال
        if status == 'مكتمل' and maintenance_request.status != 'مكتمل':
            maintenance_request.completion_date = datetime.now().strftime('%Y-%m-%d')
            
            # تحديث حالة المصعد إلى "يعمل"
            elevator = Elevator.query.get(elevator_id)
            if elevator:
                elevator.status = 'يعمل'
                elevator.last_maintenance_date = datetime.now().strftime('%Y-%m-%d')
        
        maintenance_request.status = status
        
        db.session.commit()
        
        flash('تم تحديث طلب الصيانة بنجاح', 'success')
        return redirect(url_for('requests.view', request_id=request_id))
    
    return render_template('requests/edit.html', 
                          request=maintenance_request, 
                          elevators=elevators)

# حذف طلب صيانة
@requests.route('/delete/<int:request_id>', methods=['POST'])
@login_required
def delete(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    
    # حذف جميع استخدامات قطع الغيار المرتبطة بهذا الطلب
    PartUsage.query.filter_by(request_id=request_id).delete()
    
    # حذف الطلب
    db.session.delete(maintenance_request)
    db.session.commit()
    
    flash('تم حذف طلب الصيانة بنجاح', 'success')
    return redirect(url_for('requests.index'))

# إضافة قطعة غيار إلى طلب صيانة
@requests.route('/<int:request_id>/add_part', methods=['GET', 'POST'])
@login_required
def add_part(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    parts = Part.query.all()
    
    if request.method == 'POST':
        part_id = request.form.get('part_id')
        quantity_used = request.form.get('quantity_used')
        
        # التحقق من توفر الكمية المطلوبة
        part = Part.query.get(part_id)
        if part and int(quantity_used) > part.quantity:
            flash(f'الكمية المطلوبة غير متوفرة. الكمية المتاحة: {part.quantity}', 'danger')
            return render_template('requests/add_part.html', 
                                  request=maintenance_request, 
                                  parts=parts)
        
        # إضافة استخدام قطعة الغيار
        new_usage = PartUsage(
            request_id=request_id,
            part_id=part_id,
            quantity_used=int(quantity_used),
            usage_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        db.session.add(new_usage)
        
        # تحديث كمية قطعة الغيار في المخزون
        if part:
            part.quantity -= int(quantity_used)
        
        db.session.commit()
        
        flash('تم إضافة قطعة الغيار بنجاح', 'success')
        return redirect(url_for('requests.view', request_id=request_id))
    
    return render_template('requests/add_part.html', 
                          request=maintenance_request, 
                          parts=parts)

# حذف قطعة غيار من طلب صيانة
@requests.route('/remove_part/<int:usage_id>', methods=['POST'])
@login_required
def remove_part(usage_id):
    part_usage = PartUsage.query.get_or_404(usage_id)
    request_id = part_usage.request_id
    
    # إعادة الكمية إلى المخزون
    part = Part.query.get(part_usage.part_id)
    if part:
        part.quantity += part_usage.quantity_used
    
    # حذف استخدام قطعة الغيار
    db.session.delete(part_usage)
    db.session.commit()
    
    flash('تم حذف قطعة الغيار بنجاح', 'success')
    return redirect(url_for('requests.view', request_id=request_id))

# واجهة برمجة التطبيقات لطلبات الصيانة
@requests.route('/api/list')
@login_required
def api_list():
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        maintenance_requests = MaintenanceRequest.query.order_by(MaintenanceRequest.request_date.desc()).all()
    else:
        maintenance_requests = MaintenanceRequest.query.filter_by(status=status_filter).order_by(MaintenanceRequest.request_date.desc()).all()
    
    return jsonify([req.to_dict() for req in maintenance_requests])

# واجهة برمجة التطبيقات لتفاصيل طلب صيانة
@requests.route('/api/<int:request_id>')
@login_required
def api_view(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    return jsonify(maintenance_request.to_dict())
