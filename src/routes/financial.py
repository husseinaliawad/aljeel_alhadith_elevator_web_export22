"""
مسارات المالية
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from src.models.financial.receipt import Receipt
from src.models.financial.payment import Payment
from src.models.contract import Contract
from src.models.quote import Quote
from src.models.maintenance_request import MaintenanceRequest

financial = Blueprint('financial', __name__, url_prefix='/financial')

# مسارات سندات القبض
@financial.route('/receipts')
@login_required
def receipts():
    receipts = Receipt.get_all()
    return render_template('financial/receipts/index.html', receipts=receipts)

@financial.route('/receipts/new', methods=['GET', 'POST'])
@login_required
def new_receipt():
    contracts = Contract.query.all()
    quotes = Quote.query.all()
    
    if request.method == 'POST':
        receipt_number = request.form.get('receipt_number')
        if not receipt_number:
            receipt_number = Receipt.generate_receipt_number()
            
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        client_name = request.form.get('client_name')
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method')
        reference_number = request.form.get('reference_number')
        notes = request.form.get('notes')
        created_by = current_user.full_name
        status = 'مكتمل'
        
        client_id = request.form.get('client_id') or None
        contract_id = request.form.get('contract_id') or None
        quote_id = request.form.get('quote_id') or None
        
        receipt = Receipt(
            receipt_number=receipt_number,
            date=date,
            client_id=client_id,
            client_name=client_name,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            contract_id=contract_id,
            quote_id=quote_id,
            created_by=created_by,
            status=status
        )
        
        receipt.save()
        flash('تم إضافة سند القبض بنجاح', 'success')
        return redirect(url_for('financial.receipts'))
    
    return render_template('financial/receipts/new.html', contracts=contracts, quotes=quotes)

@financial.route('/receipts/<int:id>')
@login_required
def view_receipt(id):
    receipt = Receipt.get_by_id(id)
    if not receipt:
        flash('سند القبض غير موجود', 'danger')
        return redirect(url_for('financial.receipts'))
    
    contract = None
    if receipt.contract_id:
        contract = Contract.query.get(receipt.contract_id)
        
    quote = None
    if receipt.quote_id:
        quote = Quote.query.get(receipt.quote_id)
    
    return render_template('financial/receipts/view.html', receipt=receipt, contract=contract, quote=quote)

@financial.route('/receipts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_receipt(id):
    receipt = Receipt.get_by_id(id)
    if not receipt:
        flash('سند القبض غير موجود', 'danger')
        return redirect(url_for('financial.receipts'))
    
    contracts = Contract.query.all()
    quotes = Quote.query.all()
    
    if request.method == 'POST':
        receipt.receipt_number = request.form.get('receipt_number')
        receipt.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        receipt.client_name = request.form.get('client_name')
        receipt.amount = float(request.form.get('amount'))
        receipt.payment_method = request.form.get('payment_method')
        receipt.reference_number = request.form.get('reference_number')
        receipt.notes = request.form.get('notes')
        
        receipt.client_id = request.form.get('client_id') or None
        receipt.contract_id = request.form.get('contract_id') or None
        receipt.quote_id = request.form.get('quote_id') or None
        
        receipt.save()
        flash('تم تحديث سند القبض بنجاح', 'success')
        return redirect(url_for('financial.view_receipt', id=receipt.id))
    
    return render_template('financial/receipts/edit.html', receipt=receipt, contracts=contracts, quotes=quotes)

@financial.route('/receipts/<int:id>/delete', methods=['POST'])
@login_required
def delete_receipt(id):
    receipt = Receipt.get_by_id(id)
    if not receipt:
        flash('سند القبض غير موجود', 'danger')
        return redirect(url_for('financial.receipts'))
    
    receipt.delete()
    flash('تم حذف سند القبض بنجاح', 'success')
    return redirect(url_for('financial.receipts'))

@financial.route('/receipts/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_receipt(id):
    receipt = Receipt.get_by_id(id)
    if not receipt:
        flash('سند القبض غير موجود', 'danger')
        return redirect(url_for('financial.receipts'))
    
    receipt.cancel()
    flash('تم إلغاء سند القبض بنجاح', 'success')
    return redirect(url_for('financial.view_receipt', id=receipt.id))

# مسارات سندات الصرف
@financial.route('/payments')
@login_required
def payments():
    payments = Payment.get_all()
    return render_template('financial/payments/index.html', payments=payments)

@financial.route('/payments/new', methods=['GET', 'POST'])
@login_required
def new_payment():
    contracts = Contract.query.all()
    maintenance_requests = MaintenanceRequest.query.all()
    
    if request.method == 'POST':
        payment_number = request.form.get('payment_number')
        if not payment_number:
            payment_number = Payment.generate_payment_number()
            
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        recipient_name = request.form.get('recipient_name')
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method')
        reference_number = request.form.get('reference_number')
        notes = request.form.get('notes')
        category = request.form.get('category')
        created_by = current_user.full_name
        status = 'مكتمل'
        
        recipient_id = request.form.get('recipient_id') or None
        contract_id = request.form.get('contract_id') or None
        maintenance_id = request.form.get('maintenance_id') or None
        
        payment = Payment(
            payment_number=payment_number,
            date=date,
            recipient_id=recipient_id,
            recipient_name=recipient_name,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            contract_id=contract_id,
            maintenance_id=maintenance_id,
            created_by=created_by,
            status=status,
            category=category
        )
        
        payment.save()
        flash('تم إضافة سند الصرف بنجاح', 'success')
        return redirect(url_for('financial.payments'))
    
    return render_template('financial/payments/new.html', contracts=contracts, maintenance_requests=maintenance_requests)

@financial.route('/payments/<int:id>')
@login_required
def view_payment(id):
    payment = Payment.get_by_id(id)
    if not payment:
        flash('سند الصرف غير موجود', 'danger')
        return redirect(url_for('financial.payments'))
    
    contract = None
    if payment.contract_id:
        contract = Contract.query.get(payment.contract_id)
        
    maintenance_request = None
    if payment.maintenance_id:
        maintenance_request = MaintenanceRequest.query.get(payment.maintenance_id)
    
    return render_template('financial/payments/view.html', payment=payment, contract=contract, maintenance_request=maintenance_request)

@financial.route('/payments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_payment(id):
    payment = Payment.get_by_id(id)
    if not payment:
        flash('سند الصرف غير موجود', 'danger')
        return redirect(url_for('financial.payments'))
    
    contracts = Contract.query.all()
    maintenance_requests = MaintenanceRequest.query.all()
    
    if request.method == 'POST':
        payment.payment_number = request.form.get('payment_number')
        payment.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        payment.recipient_name = request.form.get('recipient_name')
        payment.amount = float(request.form.get('amount'))
        payment.payment_method = request.form.get('payment_method')
        payment.reference_number = request.form.get('reference_number')
        payment.notes = request.form.get('notes')
        payment.category = request.form.get('category')
        
        payment.recipient_id = request.form.get('recipient_id') or None
        payment.contract_id = request.form.get('contract_id') or None
        payment.maintenance_id = request.form.get('maintenance_id') or None
        
        payment.save()
        flash('تم تحديث سند الصرف بنجاح', 'success')
        return redirect(url_for('financial.view_payment', id=payment.id))
    
    return render_template('financial/payments/edit.html', payment=payment, contracts=contracts, maintenance_requests=maintenance_requests)

@financial.route('/payments/<int:id>/delete', methods=['POST'])
@login_required
def delete_payment(id):
    payment = Payment.get_by_id(id)
    if not payment:
        flash('سند الصرف غير موجود', 'danger')
        return redirect(url_for('financial.payments'))
    
    payment.delete()
    flash('تم حذف سند الصرف بنجاح', 'success')
    return redirect(url_for('financial.payments'))

@financial.route('/payments/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_payment(id):
    payment = Payment.get_by_id(id)
    if not payment:
        flash('سند الصرف غير موجود', 'danger')
        return redirect(url_for('financial.payments'))
    
    payment.cancel()
    flash('تم إلغاء سند الصرف بنجاح', 'success')
    return redirect(url_for('financial.view_payment', id=payment.id))

# مسارات التقارير المالية
@financial.route('/reports')
@login_required
def reports():
    return render_template('financial/reports/index.html')

@financial.route('/reports/receipts', methods=['GET', 'POST'])
@login_required
def receipts_report():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        receipts = Receipt.get_by_date_range(start_date, end_date)
        
        total_amount = sum(receipt.amount for receipt in receipts if receipt.status == 'مكتمل')
        
        return render_template('financial/reports/receipts_report.html', 
                              receipts=receipts, 
                              total_amount=total_amount,
                              start_date=start_date,
                              end_date=end_date)
    
    return render_template('financial/reports/receipts_report_form.html')

@financial.route('/reports/payments', methods=['GET', 'POST'])
@login_required
def payments_report():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        category = request.form.get('category')
        
        if category and category != 'all':
            payments = Payment.get_by_category(category)
            payments = [p for p in payments if start_date <= p.date <= end_date]
        else:
            payments = Payment.get_by_date_range(start_date, end_date)
        
        total_amount = sum(payment.amount for payment in payments if payment.status == 'مكتمل')
        
        return render_template('financial/reports/payments_report.html', 
                              payments=payments, 
                              total_amount=total_amount,
                              start_date=start_date,
                              end_date=end_date,
                              category=category)
    
    return render_template('financial/reports/payments_report_form.html')
