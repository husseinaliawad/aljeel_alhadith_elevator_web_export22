"""
مسارات إدارة عروض الأسعار لتطبيق aljeel alhadith elevator
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models.quote import Quote
from src.models.contract import Contract
from src.models.price import Price
from src.routes.auth import login_required, admin_required
from src.models.db import db
from datetime import datetime, timedelta
import json

# إنشاء blueprint لعروض الأسعار
quotes = Blueprint('quotes', __name__, url_prefix='/quotes')

# عرض قائمة عروض الأسعار
@quotes.route('/')
@login_required
def index():
    # الحصول على معلمة التصفية من الاستعلام
    status_filter = request.args.get('status', 'all')
    
    # استعلام قاعدة البيانات بناءً على التصفية
    if status_filter == 'all':
        quotes = Quote.query.order_by(Quote.issue_date.desc()).all()
    else:
        quotes = Quote.query.filter_by(status=status_filter).order_by(Quote.issue_date.desc()).all()
    
    return render_template('quotes/index.html', 
                          quotes=quotes, 
                          status_filter=status_filter)

# إضافة عرض سعر جديد
@quotes.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # الحصول على قائمة الأسعار للاختيار
    prices = Price.query.all()
    
    if request.method == 'POST':
        # توليد رقم عرض سعر جديد
        quote_number = f"Q-{datetime.now().strftime('%Y%m%d')}-{Quote.query.count() + 1:03d}"
        
        client_name = request.form.get('client_name')
        client_contact = request.form.get('client_contact')
        issue_date = request.form.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
        
        # حساب تاريخ انتهاء الصلاحية (30 يوم من تاريخ الإصدار)
        valid_until = (datetime.strptime(issue_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')
        if request.form.get('valid_until'):
            valid_until = request.form.get('valid_until')
            
        notes = request.form.get('notes')
        
        # معالجة بنود عرض السعر
        items = []
        item_count = int(request.form.get('item_count', 0))
        total_amount = 0.0
        
        for i in range(item_count):
            if request.form.get(f'item_description_{i}'):
                item = {
                    'description': request.form.get(f'item_description_{i}'),
                    'quantity': float(request.form.get(f'item_quantity_{i}', 1)),
                    'unit_price': float(request.form.get(f'item_unit_price_{i}', 0)),
                    'total': float(request.form.get(f'item_total_{i}', 0))
                }
                items.append(item)
                total_amount += item['total']
        
        new_quote = Quote(
            quote_number=quote_number,
            client_name=client_name,
            client_contact=client_contact,
            issue_date=issue_date,
            valid_until=valid_until,
            total_amount=total_amount,
            status='معلق',
            items=items,
            notes=notes
        )
        
        db.session.add(new_quote)
        db.session.commit()
        
        flash('تم إضافة عرض السعر بنجاح', 'success')
        return redirect(url_for('quotes.view', quote_id=new_quote.id))
    
    return render_template('quotes/add.html', prices=prices)

# عرض تفاصيل عرض سعر
@quotes.route('/<int:quote_id>')
@login_required
def view(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    
    # الحصول على بنود عرض السعر
    items = quote.get_items()
    
    # التحقق من صلاحية العرض
    is_valid = quote.is_valid()
    
    return render_template('quotes/view.html', 
                          quote=quote, 
                          items=items,
                          is_valid=is_valid)

# تعديل عرض سعر
@quotes.route('/edit/<int:quote_id>', methods=['GET', 'POST'])
@login_required
def edit(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    prices = Price.query.all()
    
    # لا يمكن تعديل عروض الأسعار المقبولة أو المرفوضة
    if quote.status != 'معلق':
        flash('لا يمكن تعديل عرض السعر بعد قبوله أو رفضه', 'danger')
        return redirect(url_for('quotes.view', quote_id=quote.id))
    
    if request.method == 'POST':
        quote.client_name = request.form.get('client_name')
        quote.client_contact = request.form.get('client_contact')
        quote.issue_date = request.form.get('issue_date')
        quote.valid_until = request.form.get('valid_until')
        quote.notes = request.form.get('notes')
        
        # معالجة بنود عرض السعر
        items = []
        item_count = int(request.form.get('item_count', 0))
        total_amount = 0.0
        
        for i in range(item_count):
            if request.form.get(f'item_description_{i}'):
                item = {
                    'description': request.form.get(f'item_description_{i}'),
                    'quantity': float(request.form.get(f'item_quantity_{i}', 1)),
                    'unit_price': float(request.form.get(f'item_unit_price_{i}', 0)),
                    'total': float(request.form.get(f'item_total_{i}', 0))
                }
                items.append(item)
                total_amount += item['total']
        
        quote.set_items(items)
        quote.total_amount = total_amount
        
        db.session.commit()
        
        flash('تم تحديث عرض السعر بنجاح', 'success')
        return redirect(url_for('quotes.view', quote_id=quote.id))
    
    return render_template('quotes/edit.html', 
                          quote=quote, 
                          items=quote.get_items(),
                          prices=prices)

# حذف عرض سعر
@quotes.route('/delete/<int:quote_id>', methods=['POST'])
@login_required
def delete(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    
    db.session.delete(quote)
    db.session.commit()
    
    flash('تم حذف عرض السعر بنجاح', 'success')
    return redirect(url_for('quotes.index'))

# تغيير حالة عرض السعر
@quotes.route('/change_status/<int:quote_id>', methods=['POST'])
@login_required
def change_status(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    new_status = request.form.get('status')
    
    if new_status in ['معلق', 'مقبول', 'مرفوض', 'منتهي']:
        quote.status = new_status
        db.session.commit()
        
        status_message = {
            'معلق': 'تم تعليق',
            'مقبول': 'تم قبول',
            'مرفوض': 'تم رفض',
            'منتهي': 'تم إنهاء'
        }
        
        flash(f"{status_message[new_status]} عرض السعر بنجاح", 'success')
    else:
        flash('حالة غير صالحة', 'danger')
    
    return redirect(url_for('quotes.view', quote_id=quote.id))

# تحويل عرض السعر إلى عقد
@quotes.route('/convert_to_contract/<int:quote_id>', methods=['GET', 'POST'])
@login_required
def convert_to_contract(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    
    # التحقق من أن عرض السعر مقبول
    if quote.status != 'مقبول':
        flash('يمكن تحويل عروض الأسعار المقبولة فقط إلى عقود', 'danger')
        return redirect(url_for('quotes.view', quote_id=quote.id))
    
    if request.method == 'POST':
        # توليد رقم عقد جديد
        contract_number = f"C-{datetime.now().strftime('%Y%m')}-{Contract.query.count() + 1:03d}"
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        contract_type = request.form.get('contract_type')
        payment_terms = request.form.get('payment_terms')
        elevator_ids = request.form.getlist('elevator_ids')
        notes = request.form.get('notes', '')
        
        new_contract = Contract(
            contract_number=contract_number,
            client_name=quote.client_name,
            start_date=start_date,
            end_date=end_date,
            contract_type=contract_type,
            contract_value=quote.total_amount,
            payment_terms=payment_terms,
            elevator_ids=elevator_ids,
            status='ساري',
            notes=f"تم إنشاؤه من عرض السعر رقم {quote.quote_number}. {notes}"
        )
        
        db.session.add(new_contract)
        
        # تحديث حالة عرض السعر
        quote.status = 'مقبول'
        
        db.session.commit()
        
        flash('تم تحويل عرض السعر إلى عقد بنجاح', 'success')
        return redirect(url_for('contracts.view', contract_id=new_contract.id))
    
    # الحصول على قائمة المصاعد للاختيار
    from src.models.elevator import Elevator
    elevators = Elevator.query.all()
    
    # اقتراح تاريخ بداية ونهاية للعقد
    suggested_start_date = datetime.now().strftime('%Y-%m-%d')
    suggested_end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    
    return render_template('quotes/convert_to_contract.html', 
                          quote=quote,
                          elevators=elevators,
                          suggested_start_date=suggested_start_date,
                          suggested_end_date=suggested_end_date)

# طباعة عرض السعر
@quotes.route('/print/<int:quote_id>')
@login_required
def print_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    items = quote.get_items()
    
    return render_template('quotes/print.html', 
                          quote=quote, 
                          items=items)

# واجهة برمجة التطبيقات لعروض الأسعار
@quotes.route('/api/list')
@login_required
def api_list():
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        quotes = Quote.query.order_by(Quote.issue_date.desc()).all()
    else:
        quotes = Quote.query.filter_by(status=status_filter).order_by(Quote.issue_date.desc()).all()
    
    return jsonify([quote.to_dict() for quote in quotes])

# واجهة برمجة التطبيقات لتفاصيل عرض سعر
@quotes.route('/api/<int:quote_id>')
@login_required
def api_view(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    return jsonify(quote.to_dict())
