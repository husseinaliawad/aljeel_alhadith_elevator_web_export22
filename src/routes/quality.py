"""
مسارات الجودة والامتثال
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from src.models.quality_compliance.inspection import Inspection
from src.models.quality_compliance.safety_certificate import SafetyCertificate
from src.models.quality_compliance.compliance import ComplianceStandard, ElevatorCompliance
from src.models.elevator import Elevator

quality = Blueprint('quality', __name__, url_prefix='/quality')

# مسارات الفحوصات
@quality.route('/inspections')
@login_required
def inspections():
    inspections = Inspection.get_all()
    return render_template('quality/inspections/index.html', inspections=inspections)

@quality.route('/inspections/new', methods=['GET', 'POST'])
@login_required
def new_inspection():
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        elevator_id = request.form.get('elevator_id')
        inspector_name = request.form.get('inspector_name')
        inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d').date()
        inspection_type = request.form.get('inspection_type')
        status = request.form.get('status')
        notes = request.form.get('notes')
        compliance_status = request.form.get('compliance_status')
        
        next_inspection_date = None
        if request.form.get('next_inspection_date'):
            next_inspection_date = datetime.strptime(request.form.get('next_inspection_date'), '%Y-%m-%d').date()
        
        inspection = Inspection(
            elevator_id=elevator_id,
            inspector_name=inspector_name,
            inspection_date=inspection_date,
            inspection_type=inspection_type,
            status=status,
            notes=notes,
            compliance_status=compliance_status,
            next_inspection_date=next_inspection_date
        )
        
        inspection.save()
        flash('تم إضافة الفحص بنجاح', 'success')
        return redirect(url_for('quality.inspections'))
    
    return render_template('quality/inspections/new.html', elevators=elevators)

@quality.route('/inspections/<int:id>')
@login_required
def view_inspection(id):
    inspection = Inspection.get_by_id(id)
    if not inspection:
        flash('الفحص غير موجود', 'danger')
        return redirect(url_for('quality.inspections'))
    
    elevator = Elevator.query.get(inspection.elevator_id)
    return render_template('quality/inspections/view.html', inspection=inspection, elevator=elevator)

@quality.route('/inspections/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inspection(id):
    inspection = Inspection.get_by_id(id)
    if not inspection:
        flash('الفحص غير موجود', 'danger')
        return redirect(url_for('quality.inspections'))
    
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        inspection.elevator_id = request.form.get('elevator_id')
        inspection.inspector_name = request.form.get('inspector_name')
        inspection.inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d').date()
        inspection.inspection_type = request.form.get('inspection_type')
        inspection.status = request.form.get('status')
        inspection.notes = request.form.get('notes')
        inspection.compliance_status = request.form.get('compliance_status')
        
        if request.form.get('next_inspection_date'):
            inspection.next_inspection_date = datetime.strptime(request.form.get('next_inspection_date'), '%Y-%m-%d').date()
        else:
            inspection.next_inspection_date = None
        
        inspection.save()
        flash('تم تحديث الفحص بنجاح', 'success')
        return redirect(url_for('quality.view_inspection', id=inspection.id))
    
    return render_template('quality/inspections/edit.html', inspection=inspection, elevators=elevators)

@quality.route('/inspections/<int:id>/delete', methods=['POST'])
@login_required
def delete_inspection(id):
    inspection = Inspection.get_by_id(id)
    if not inspection:
        flash('الفحص غير موجود', 'danger')
        return redirect(url_for('quality.inspections'))
    
    inspection.delete()
    flash('تم حذف الفحص بنجاح', 'success')
    return redirect(url_for('quality.inspections'))

# مسارات شهادات السلامة
@quality.route('/certificates')
@login_required
def certificates():
    certificates = SafetyCertificate.get_all()
    return render_template('quality/certificates/index.html', certificates=certificates)

@quality.route('/certificates/new', methods=['GET', 'POST'])
@login_required
def new_certificate():
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        elevator_id = request.form.get('elevator_id')
        certificate_number = request.form.get('certificate_number')
        if not certificate_number:
            certificate_number = SafetyCertificate.generate_certificate_number(elevator_id)
            
        issue_date = datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date()
        expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
        issuing_authority = request.form.get('issuing_authority')
        certificate_type = request.form.get('certificate_type')
        status = request.form.get('status')
        notes = request.form.get('notes')
        issued_by = request.form.get('issued_by')
        
        certificate = SafetyCertificate(
            elevator_id=elevator_id,
            certificate_number=certificate_number,
            issue_date=issue_date,
            expiry_date=expiry_date,
            issuing_authority=issuing_authority,
            certificate_type=certificate_type,
            status=status,
            notes=notes,
            issued_by=issued_by
        )
        
        certificate.save()
        flash('تم إضافة شهادة السلامة بنجاح', 'success')
        return redirect(url_for('quality.certificates'))
    
    return render_template('quality/certificates/new.html', elevators=elevators)

@quality.route('/certificates/<int:id>')
@login_required
def view_certificate(id):
    certificate = SafetyCertificate.get_by_id(id)
    if not certificate:
        flash('شهادة السلامة غير موجودة', 'danger')
        return redirect(url_for('quality.certificates'))
    
    elevator = Elevator.query.get(certificate.elevator_id)
    return render_template('quality/certificates/view.html', certificate=certificate, elevator=elevator)

@quality.route('/certificates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_certificate(id):
    certificate = SafetyCertificate.get_by_id(id)
    if not certificate:
        flash('شهادة السلامة غير موجودة', 'danger')
        return redirect(url_for('quality.certificates'))
    
    elevators = Elevator.query.all()
    
    if request.method == 'POST':
        certificate.elevator_id = request.form.get('elevator_id')
        certificate.certificate_number = request.form.get('certificate_number')
        certificate.issue_date = datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d').date()
        certificate.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
        certificate.issuing_authority = request.form.get('issuing_authority')
        certificate.certificate_type = request.form.get('certificate_type')
        certificate.status = request.form.get('status')
        certificate.notes = request.form.get('notes')
        certificate.issued_by = request.form.get('issued_by')
        
        certificate.save()
        flash('تم تحديث شهادة السلامة بنجاح', 'success')
        return redirect(url_for('quality.view_certificate', id=certificate.id))
    
    return render_template('quality/certificates/edit.html', certificate=certificate, elevators=elevators)

@quality.route('/certificates/<int:id>/delete', methods=['POST'])
@login_required
def delete_certificate(id):
    certificate = SafetyCertificate.get_by_id(id)
    if not certificate:
        flash('شهادة السلامة غير موجودة', 'danger')
        return redirect(url_for('quality.certificates'))
    
    certificate.delete()
    flash('تم حذف شهادة السلامة بنجاح', 'success')
    return redirect(url_for('quality.certificates'))

# مسارات متابعة الامتثال
@quality.route('/compliance')
@login_required
def compliance():
    standards = ComplianceStandard.get_all()
    return render_template('quality/compliance/index.html', standards=standards)

@quality.route('/compliance/standards/new', methods=['GET', 'POST'])
@login_required
def new_standard():
    if request.method == 'POST':
        standard_name = request.form.get('standard_name')
        standard_code = request.form.get('standard_code')
        issuing_body = request.form.get('issuing_body')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        effective_date = datetime.strptime(request.form.get('effective_date'), '%Y-%m-%d').date()
        status = request.form.get('status')
        
        standard = ComplianceStandard(
            standard_name=standard_name,
            standard_code=standard_code,
            issuing_body=issuing_body,
            description=description,
            requirements=requirements,
            effective_date=effective_date,
            status=status
        )
        
        standard.save()
        flash('تم إضافة معيار الامتثال بنجاح', 'success')
        return redirect(url_for('quality.compliance'))
    
    return render_template('quality/compliance/new_standard.html')

@quality.route('/compliance/elevator/<int:elevator_id>')
@login_required
def elevator_compliance(elevator_id):
    elevator = Elevator.query.get(elevator_id)
    if not elevator:
        flash('المصعد غير موجود', 'danger')
        return redirect(url_for('elevators.index'))
    
    compliance_records = ElevatorCompliance.get_by_elevator_id(elevator_id)
    return render_template('quality/compliance/elevator.html', elevator=elevator, compliance_records=compliance_records)

@quality.route('/compliance/elevator/<int:elevator_id>/new', methods=['GET', 'POST'])
@login_required
def new_elevator_compliance(elevator_id):
    elevator = Elevator.query.get(elevator_id)
    if not elevator:
        flash('المصعد غير موجود', 'danger')
        return redirect(url_for('elevators.index'))
    
    standards = ComplianceStandard.get_active_standards()
    
    if request.method == 'POST':
        standard_id = request.form.get('standard_id')
        compliance_status = request.form.get('compliance_status')
        last_check_date = datetime.strptime(request.form.get('last_check_date'), '%Y-%m-%d').date()
        notes = request.form.get('notes')
        checked_by = request.form.get('checked_by')
        
        next_check_date = None
        if request.form.get('next_check_date'):
            next_check_date = datetime.strptime(request.form.get('next_check_date'), '%Y-%m-%d').date()
        
        compliance = ElevatorCompliance(
            elevator_id=elevator_id,
            standard_id=standard_id,
            compliance_status=compliance_status,
            last_check_date=last_check_date,
            next_check_date=next_check_date,
            notes=notes,
            checked_by=checked_by
        )
        
        compliance.save()
        flash('تم إضافة سجل امتثال المصعد بنجاح', 'success')
        return redirect(url_for('quality.elevator_compliance', elevator_id=elevator_id))
    
    return render_template('quality/compliance/new_elevator_compliance.html', elevator=elevator, standards=standards)
