"""
مسارات إدارة العقود لتطبيق aljeel alhadith elevator
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.contract import Contract
from src.models.elevator import Elevator
from src.routes.auth import login_required, admin_required
from src.models.db import db
from datetime import datetime, timedelta
import json

# إنشاء blueprint للعقود
contracts = Blueprint('contracts', __name__, url_prefix='/contracts')

# عرض قائمة العقود
@contracts.route('/')
@login_required
def index():
    # الحصول على معلمة التصفية من الاستعلام
    status_filter = request.args.get('status', 'all')
    
    # استعلام قاعدة البيانات بناءً على التصفية
    if status_filter == 'all':
        contracts = Contract.query.order_by(Contract.start_date.desc()).all()
    else:
        contracts = Contract.query.filter_by(status=status_filter).order_by(Contract.start_date.desc()).all()
    
    return render_template('contracts/index.html', 
                          contracts=contracts, 
                          status_filter=status_filter)

# إضافة عقد جديد
@contracts.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # الحصول على قائمة المصاعد للاختيار
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        contract_number = request.form.get('contract_number')
        client_name = request.form.get('client_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        contract_type = request.form.get('contract_type')
        contract_value = float(request.form.get('contract_value', 0.0))
        payment_terms = request.form.get('payment_terms')
        status = request.form.get('status', 'ساري')
        notes = request.form.get('notes')
        
        # الحصول على المصاعد المحددة
        elevator_ids = request.form.getlist('elevator_ids')
        
        new_contract = Contract(
            contract_number=contract_number,
            client_name=client_name,
            start_date=start_date,
            end_date=end_date,
            contract_type=contract_type,
            contract_value=contract_value,
            payment_terms=payment_terms,
            elevator_ids=elevator_ids,
            status=status,
            notes=notes
        )
        
        db.session.add(new_contract)
        db.session.commit()
        
        flash('تم إضافة العقد بنجاح', 'success')
        return redirect(url_for('contracts.index'))
    
    return render_template('contracts/add.html', elevators=elevators)

# عرض تفاصيل عقد
@contracts.route('/<int:contract_id>')
@login_required
def view(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    
    # الحصول على المصاعد المرتبطة بالعقد
    elevator_ids = contract.get_elevator_ids()
    elevators = Elevator.query.filter(Elevator.id.in_(elevator_ids)).all() if elevator_ids else []
    
    # حساب عدد الأيام المتبقية حتى انتهاء العقد
    days_remaining = contract.days_until_expiry()
    
    return render_template('contracts/view.html', 
                          contract=contract, 
                          elevators=elevators,
                          days_remaining=days_remaining)

# تعديل عقد
@contracts.route('/edit/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def edit(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        contract.contract_number = request.form.get('contract_number')
        contract.client_name = request.form.get('client_name')
        contract.start_date = request.form.get('start_date')
        contract.end_date = request.form.get('end_date')
        contract.contract_type = request.form.get('contract_type')
        contract.contract_value = float(request.form.get('contract_value', 0.0))
        contract.payment_terms = request.form.get('payment_terms')
        contract.status = request.form.get('status')
        contract.notes = request.form.get('notes')
        
        # تحديث المصاعد المرتبطة بالعقد
        elevator_ids = request.form.getlist('elevator_ids')
        contract.set_elevator_ids(elevator_ids)
        
        db.session.commit()
        
        flash('تم تحديث العقد بنجاح', 'success')
        return redirect(url_for('contracts.view', contract_id=contract.id))
    
    return render_template('contracts/edit.html', 
                          contract=contract, 
                          elevators=elevators,
                          selected_elevator_ids=contract.get_elevator_ids())

# حذف عقد
@contracts.route('/delete/<int:contract_id>', methods=['POST'])
@login_required
def delete(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    
    db.session.delete(contract)
    db.session.commit()
    
    flash('تم حذف العقد بنجاح', 'success')
    return redirect(url_for('contracts.index'))

# تجديد عقد
@contracts.route('/renew/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def renew(contract_id):
    old_contract = Contract.query.get_or_404(contract_id)
    
    if request.method == 'POST':
        # إنشاء رقم عقد جديد
        new_contract_number = f"{old_contract.contract_number}-R{datetime.now().strftime('%y%m')}"
        
        # الحصول على تواريخ العقد الجديد
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        contract_value = float(request.form.get('contract_value', old_contract.contract_value))
        payment_terms = request.form.get('payment_terms', old_contract.payment_terms)
        notes = request.form.get('notes', '')
        
        # إنشاء عقد جديد
        new_contract = Contract(
            contract_number=new_contract_number,
            client_name=old_contract.client_name,
            start_date=start_date,
            end_date=end_date,
            contract_type=old_contract.contract_type,
            contract_value=contract_value,
            payment_terms=payment_terms,
            elevator_ids=old_contract.get_elevator_ids(),
            status='ساري',
            notes=f"تجديد للعقد رقم {old_contract.contract_number}. {notes}"
        )
        
        # تحديث حالة العقد القديم
        old_contract.status = 'منتهي'
        
        db.session.add(new_contract)
        db.session.commit()
        
        flash('تم تجديد العقد بنجاح', 'success')
        return redirect(url_for('contracts.view', contract_id=new_contract.id))
    
    # اقتراح تاريخ بداية ونهاية للعقد الجديد
    suggested_start_date = datetime.now().strftime('%Y-%m-%d')
    suggested_end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    
    return render_template('contracts/renew.html', 
                          contract=old_contract,
                          suggested_start_date=suggested_start_date,
                          suggested_end_date=suggested_end_date)

# تقرير العقود
@contracts.route('/report')
@login_required
def report():
    # الحصول على جميع العقود
    all_contracts = Contract.query.all()
    
    # العقود السارية
    active_contracts = [c for c in all_contracts if c.is_active()]
    
    # العقود المنتهية
    expired_contracts = [c for c in all_contracts if c.status == 'منتهي']
    
    # العقود التي ستنتهي خلال 30 يوم
    today = datetime.now()
    thirty_days_later = today + timedelta(days=30)
    expiring_soon = [c for c in active_contracts if c.end_date <= thirty_days_later.strftime('%Y-%m-%d')]
    
    # إجمالي قيمة العقود السارية
    total_active_value = sum(c.contract_value for c in active_contracts)
    
    return render_template('contracts/report.html',
                          active_contracts=active_contracts,
                          expired_contracts=expired_contracts,
                          expiring_soon=expiring_soon,
                          total_active_value=total_active_value)

# واجهة برمجة التطبيقات للعقود
@contracts.route('/api/list')
@login_required
def api_list():
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        contracts = Contract.query.order_by(Contract.start_date.desc()).all()
    else:
        contracts = Contract.query.filter_by(status=status_filter).order_by(Contract.start_date.desc()).all()
    
    return jsonify([contract.to_dict() for contract in contracts])

# واجهة برمجة التطبيقات لتفاصيل عقد
@contracts.route('/api/<int:contract_id>')
@login_required
def api_view(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return jsonify(contract.to_dict())
