"""
مسارات إدارة المصاعد لتطبيق aljeel alhadith elevator
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.elevator import Elevator
from src.models.maintenance_request import MaintenanceRequest
from src.models.scheduled_maintenance import ScheduledMaintenance
from src.routes.auth import login_required
from src.models.db import db
from datetime import datetime

# إنشاء blueprint للمصاعد
elevators = Blueprint('elevators', __name__, url_prefix='/elevators')

# عرض قائمة المصاعد
@elevators.route('/')
# @login_required - تم إزالة متطلب تسجيل الدخول مؤقتاً
def index():
    elevators = Elevator.query.all()
    return render_template('elevators/index.html', elevators=elevators)

# إضافة مصعد جديد
@elevators.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        building_name = request.form.get('building_name')
        model = request.form.get('model')
        installation_date = request.form.get('installation_date')
        last_maintenance_date = request.form.get('last_maintenance_date')
        maintenance_interval = request.form.get('maintenance_interval', 90)
        status = request.form.get('status', 'يعمل')
        
        new_elevator = Elevator(
            building_name=building_name,
            model=model,
            installation_date=installation_date,
            last_maintenance_date=last_maintenance_date,
            maintenance_interval=int(maintenance_interval),
            status=status
        )
        
        db.session.add(new_elevator)
        db.session.commit()
        
        flash('تم إضافة المصعد بنجاح', 'success')
        return redirect(url_for('elevators.index'))
    
    return render_template('elevators/add.html')

# عرض تفاصيل مصعد
@elevators.route('/<int:elevator_id>')
@login_required
def view(elevator_id):
    elevator = Elevator.query.get_or_404(elevator_id)
    
    # الحصول على طلبات الصيانة المرتبطة بالمصعد
    maintenance_requests = MaintenanceRequest.query.filter_by(elevator_id=elevator_id).order_by(MaintenanceRequest.request_date.desc()).all()
    
    # الحصول على الصيانة الدورية المجدولة للمصعد
    scheduled_maintenance = ScheduledMaintenance.query.filter_by(elevator_id=elevator_id).order_by(ScheduledMaintenance.scheduled_date.desc()).all()
    
    return render_template('elevators/view.html', 
                          elevator=elevator, 
                          maintenance_requests=maintenance_requests,
                          scheduled_maintenance=scheduled_maintenance)

# تعديل مصعد
@elevators.route('/edit/<int:elevator_id>', methods=['GET', 'POST'])
@login_required
def edit(elevator_id):
    elevator = Elevator.query.get_or_404(elevator_id)
    
    if request.method == 'POST':
        elevator.building_name = request.form.get('building_name')
        elevator.model = request.form.get('model')
        elevator.installation_date = request.form.get('installation_date')
        elevator.last_maintenance_date = request.form.get('last_maintenance_date')
        elevator.maintenance_interval = int(request.form.get('maintenance_interval', 90))
        elevator.status = request.form.get('status')
        
        db.session.commit()
        
        flash('تم تحديث بيانات المصعد بنجاح', 'success')
        return redirect(url_for('elevators.view', elevator_id=elevator.id))
    
    return render_template('elevators/edit.html', elevator=elevator)

# حذف مصعد
@elevators.route('/delete/<int:elevator_id>', methods=['POST'])
@login_required
def delete(elevator_id):
    elevator = Elevator.query.get_or_404(elevator_id)
    
    # التحقق من عدم وجود طلبات صيانة مرتبطة بالمصعد
    maintenance_requests = MaintenanceRequest.query.filter_by(elevator_id=elevator_id).count()
    if maintenance_requests > 0:
        flash('لا يمكن حذف المصعد لوجود طلبات صيانة مرتبطة به', 'danger')
        return redirect(url_for('elevators.view', elevator_id=elevator.id))
    
    # التحقق من عدم وجود صيانة دورية مجدولة للمصعد
    scheduled_maintenance = ScheduledMaintenance.query.filter_by(elevator_id=elevator_id).count()
    if scheduled_maintenance > 0:
        flash('لا يمكن حذف المصعد لوجود صيانة دورية مجدولة له', 'danger')
        return redirect(url_for('elevators.view', elevator_id=elevator.id))
    
    db.session.delete(elevator)
    db.session.commit()
    
    flash('تم حذف المصعد بنجاح', 'success')
    return redirect(url_for('elevators.index'))

# جدولة صيانة دورية
@elevators.route('/<int:elevator_id>/schedule', methods=['GET', 'POST'])
@login_required
def schedule_maintenance(elevator_id):
    elevator = Elevator.query.get_or_404(elevator_id)
    
    if request.method == 'POST':
        scheduled_date = request.form.get('scheduled_date')
        maintenance_type = request.form.get('maintenance_type')
        notes = request.form.get('notes')
        
        new_schedule = ScheduledMaintenance(
            elevator_id=elevator_id,
            scheduled_date=scheduled_date,
            maintenance_type=maintenance_type,
            status='مجدولة',
            notes=notes
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        
        flash('تم جدولة الصيانة الدورية بنجاح', 'success')
        return redirect(url_for('elevators.view', elevator_id=elevator.id))
    
    return render_template('elevators/schedule_maintenance.html', elevator=elevator)

# إنشاء طلب صيانة جديد
@elevators.route('/<int:elevator_id>/request', methods=['GET', 'POST'])
@login_required
def create_request(elevator_id):
    elevator = Elevator.query.get_or_404(elevator_id)
    
    if request.method == 'POST':
        issue_description = request.form.get('issue_description')
        priority = request.form.get('priority')
        
        new_request = MaintenanceRequest(
            request_date=datetime.now().strftime('%Y-%m-%d'),
            building_name=elevator.building_name,
            elevator_id=elevator_id,
            issue_description=issue_description,
            priority=priority,
            status='جديد'
        )
        
        db.session.add(new_request)
        
        # تحديث حالة المصعد إلى "قيد الصيانة"
        elevator.status = 'قيد الصيانة'
        
        db.session.commit()
        
        flash('تم إنشاء طلب الصيانة بنجاح', 'success')
        return redirect(url_for('elevators.view', elevator_id=elevator.id))
    
    return render_template('elevators/create_request.html', elevator=elevator)

# واجهة برمجة التطبيقات للمصاعد
@elevators.route('/api/list')
@login_required
def api_list():
    elevators = Elevator.query.all()
    return jsonify([elevator.to_dict() for elevator in elevators])

# واجهة برمجة التطبيقات لتفاصيل مصعد
@elevators.route('/api/<int:elevator_id>')
@login_required
def api_view(elevator_id):
    elevator = Elevator.query.get_or_404(elevator_id)
    return jsonify(elevator.to_dict())
