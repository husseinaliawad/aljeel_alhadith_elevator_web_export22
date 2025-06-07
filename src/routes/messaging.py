"""
مسارات إرسال الرسائل عبر البريد الإلكتروني والواتساب
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from src.models.messaging import MessageLog, EmailTemplate, WhatsAppTemplate
from src.models.db import db
from src.services.messaging_service import MessagingService
from src.routes.auth import login_required, admin_required
from datetime import datetime

# إنشاء blueprint للرسائل
messaging = Blueprint('messaging', __name__)

# صفحة سجل الرسائل
@messaging.route('/messages/logs')
@admin_required
def message_logs():
    logs = MessageLog.query.order_by(MessageLog.created_at.desc()).all()
    return render_template('messaging/logs.html', logs=logs)

# صفحة قوالب البريد الإلكتروني
@messaging.route('/messages/email-templates')
@admin_required
def email_templates():
    templates = EmailTemplate.query.all()
    return render_template('messaging/email_templates.html', templates=templates)

# إضافة قالب بريد إلكتروني جديد
@messaging.route('/messages/email-templates/add', methods=['GET', 'POST'])
@admin_required
def add_email_template():
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        # التحقق من عدم وجود قالب بنفس الاسم
        existing_template = EmailTemplate.query.filter_by(name=name).first()
        if existing_template:
            flash('يوجد قالب بنفس الاسم بالفعل', 'danger')
            return render_template('messaging/add_email_template.html')
        
        new_template = EmailTemplate(
            name=name,
            subject=subject,
            body=body
        )
        
        db.session.add(new_template)
        db.session.commit()
        
        flash('تم إضافة قالب البريد الإلكتروني بنجاح', 'success')
        return redirect(url_for('messaging.email_templates'))
    
    return render_template('messaging/add_email_template.html')

# تعديل قالب بريد إلكتروني
@messaging.route('/messages/email-templates/edit/<int:template_id>', methods=['GET', 'POST'])
@admin_required
def edit_email_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        template.name = request.form.get('name')
        template.subject = request.form.get('subject')
        template.body = request.form.get('body')
        template.is_active = 'is_active' in request.form
        
        db.session.commit()
        
        flash('تم تحديث قالب البريد الإلكتروني بنجاح', 'success')
        return redirect(url_for('messaging.email_templates'))
    
    return render_template('messaging/edit_email_template.html', template=template)

# حذف قالب بريد إلكتروني
@messaging.route('/messages/email-templates/delete/<int:template_id>', methods=['POST'])
@admin_required
def delete_email_template(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    
    db.session.delete(template)
    db.session.commit()
    
    flash('تم حذف قالب البريد الإلكتروني بنجاح', 'success')
    return redirect(url_for('messaging.email_templates'))

# صفحة قوالب الواتساب
@messaging.route('/messages/whatsapp-templates')
@admin_required
def whatsapp_templates():
    templates = WhatsAppTemplate.query.all()
    return render_template('messaging/whatsapp_templates.html', templates=templates)

# إضافة قالب واتساب جديد
@messaging.route('/messages/whatsapp-templates/add', methods=['GET', 'POST'])
@admin_required
def add_whatsapp_template():
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        
        # التحقق من عدم وجود قالب بنفس الاسم
        existing_template = WhatsAppTemplate.query.filter_by(name=name).first()
        if existing_template:
            flash('يوجد قالب بنفس الاسم بالفعل', 'danger')
            return render_template('messaging/add_whatsapp_template.html')
        
        new_template = WhatsAppTemplate(
            name=name,
            message=message
        )
        
        db.session.add(new_template)
        db.session.commit()
        
        flash('تم إضافة قالب الواتساب بنجاح', 'success')
        return redirect(url_for('messaging.whatsapp_templates'))
    
    return render_template('messaging/add_whatsapp_template.html')

# تعديل قالب واتساب
@messaging.route('/messages/whatsapp-templates/edit/<int:template_id>', methods=['GET', 'POST'])
@admin_required
def edit_whatsapp_template(template_id):
    template = WhatsAppTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        template.name = request.form.get('name')
        template.message = request.form.get('message')
        template.is_active = 'is_active' in request.form
        
        db.session.commit()
        
        flash('تم تحديث قالب الواتساب بنجاح', 'success')
        return redirect(url_for('messaging.whatsapp_templates'))
    
    return render_template('messaging/edit_whatsapp_template.html', template=template)

# حذف قالب واتساب
@messaging.route('/messages/whatsapp-templates/delete/<int:template_id>', methods=['POST'])
@admin_required
def delete_whatsapp_template(template_id):
    template = WhatsAppTemplate.query.get_or_404(template_id)
    
    db.session.delete(template)
    db.session.commit()
    
    flash('تم حذف قالب الواتساب بنجاح', 'success')
    return redirect(url_for('messaging.whatsapp_templates'))

# إرسال عقد عبر البريد الإلكتروني
@messaging.route('/contracts/<int:contract_id>/send-email', methods=['GET', 'POST'])
@login_required
def send_contract_email(contract_id):
    from src.models.contract import Contract
    contract = Contract.query.get_or_404(contract_id)
    
    if request.method == 'POST':
        recipient_email = request.form.get('email')
        template_name = request.form.get('template')
        
        success = MessagingService.send_document_by_email(
            document_type='contract',
            document_id=contract_id,
            recipient_email=recipient_email,
            template_name=template_name
        )
        
        if success:
            flash('تم إرسال العقد بنجاح عبر البريد الإلكتروني', 'success')
        else:
            flash('فشل إرسال العقد عبر البريد الإلكتروني', 'danger')
        
        return redirect(url_for('contracts.view_contract', contract_id=contract_id))
    
    templates = EmailTemplate.query.filter_by(is_active=True).all()
    return render_template('messaging/send_email.html', 
                          document=contract, 
                          document_type='contract',
                          templates=templates,
                          recipient_email=contract.client_email if hasattr(contract, 'client_email') else '')

# إرسال عقد عبر الواتساب
@messaging.route('/contracts/<int:contract_id>/send-whatsapp', methods=['GET', 'POST'])
@login_required
def send_contract_whatsapp(contract_id):
    from src.models.contract import Contract
    contract = Contract.query.get_or_404(contract_id)
    
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        template_name = request.form.get('template')
        
        # تنظيف رقم الهاتف (إزالة الرمز + والمسافات)
        phone_number = phone_number.replace('+', '').replace(' ', '')
        
        whatsapp_link = MessagingService.get_document_whatsapp_link(
            document_type='contract',
            document_id=contract_id,
            phone_number=phone_number,
            template_name=template_name
        )
        
        if whatsapp_link:
            # تخزين الرابط في الجلسة للاستخدام في صفحة التأكيد
            session['whatsapp_link'] = whatsapp_link
            return redirect(url_for('messaging.whatsapp_confirm'))
        else:
            flash('فشل إنشاء رابط الواتساب', 'danger')
            return redirect(url_for('contracts.view_contract', contract_id=contract_id))
    
    templates = WhatsAppTemplate.query.filter_by(is_active=True).all()
    return render_template('messaging/send_whatsapp.html', 
                          document=contract, 
                          document_type='contract',
                          templates=templates,
                          recipient_phone=contract.client_phone if hasattr(contract, 'client_phone') else '')

# إرسال عرض سعر عبر البريد الإلكتروني
@messaging.route('/quotes/<int:quote_id>/send-email', methods=['GET', 'POST'])
@login_required
def send_quote_email(quote_id):
    from src.models.quote import Quote
    quote = Quote.query.get_or_404(quote_id)
    
    if request.method == 'POST':
        recipient_email = request.form.get('email')
        template_name = request.form.get('template')
        
        success = MessagingService.send_document_by_email(
            document_type='quote',
            document_id=quote_id,
            recipient_email=recipient_email,
            template_name=template_name
        )
        
        if success:
            flash('تم إرسال عرض السعر بنجاح عبر البريد الإلكتروني', 'success')
        else:
            flash('فشل إرسال عرض السعر عبر البريد الإلكتروني', 'danger')
        
        return redirect(url_for('quotes.view_quote', quote_id=quote_id))
    
    templates = EmailTemplate.query.filter_by(is_active=True).all()
    return render_template('messaging/send_email.html', 
                          document=quote, 
                          document_type='quote',
                          templates=templates,
                          recipient_email=quote.client_email if hasattr(quote, 'client_email') else '')

# إرسال عرض سعر عبر الواتساب
@messaging.route('/quotes/<int:quote_id>/send-whatsapp', methods=['GET', 'POST'])
@login_required
def send_quote_whatsapp(quote_id):
    from src.models.quote import Quote
    quote = Quote.query.get_or_404(quote_id)
    
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        template_name = request.form.get('template')
        
        # تنظيف رقم الهاتف (إزالة الرمز + والمسافات)
        phone_number = phone_number.replace('+', '').replace(' ', '')
        
        whatsapp_link = MessagingService.get_document_whatsapp_link(
            document_type='quote',
            document_id=quote_id,
            phone_number=phone_number,
            template_name=template_name
        )
        
        if whatsapp_link:
            # تخزين الرابط في الجلسة للاستخدام في صفحة التأكيد
            session['whatsapp_link'] = whatsapp_link
            return redirect(url_for('messaging.whatsapp_confirm'))
        else:
            flash('فشل إنشاء رابط الواتساب', 'danger')
            return redirect(url_for('quotes.view_quote', quote_id=quote_id))
    
    templates = WhatsAppTemplate.query.filter_by(is_active=True).all()
    return render_template('messaging/send_whatsapp.html', 
                          document=quote, 
                          document_type='quote',
                          templates=templates,
                          recipient_phone=quote.client_phone if hasattr(quote, 'client_phone') else '')

# إرسال إيصال عبر البريد الإلكتروني
@messaging.route('/receipts/<int:receipt_id>/send-email', methods=['GET', 'POST'])
@login_required
def send_receipt_email(receipt_id):
    from src.models.financial.receipt import Receipt
    receipt = Receipt.query.get_or_404(receipt_id)
    
    if request.method == 'POST':
        recipient_email = request.form.get('email')
        template_name = request.form.get('template')
        
        success = MessagingService.send_document_by_email(
            document_type='receipt',
            document_id=receipt_id,
            recipient_email=recipient_email,
            template_name=template_name
        )
        
        if success:
            flash('تم إرسال الإيصال بنجاح عبر البريد الإلكتروني', 'success')
        else:
            flash('فشل إرسال الإيصال عبر البريد الإلكتروني', 'danger')
        
        return redirect(url_for('financial.view_receipt', receipt_id=receipt_id))
    
    templates = EmailTemplate.query.filter_by(is_active=True).all()
    return render_template('messaging/send_email.html', 
                          document=receipt, 
                          document_type='receipt',
                          templates=templates,
                          recipient_email=receipt.client_email if hasattr(receipt, 'client_email') else '')

# إرسال إيصال عبر الواتساب
@messaging.route('/receipts/<int:receipt_id>/send-whatsapp', methods=['GET', 'POST'])
@login_required
def send_receipt_whatsapp(receipt_id):
    from src.models.financial.receipt import Receipt
    receipt = Receipt.query.get_or_404(receipt_id)
    
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        template_name = request.form.get('template')
        
        # تنظيف رقم الهاتف (إزالة الرمز + والمسافات)
        phone_number = phone_number.replace('+', '').replace(' ', '')
        
        whatsapp_link = MessagingService.get_document_whatsapp_link(
            document_type='receipt',
            document_id=receipt_id,
            phone_number=phone_number,
            template_name=template_name
        )
        
        if whatsapp_link:
            # تخزين الرابط في الجلسة للاستخدام في صفحة التأكيد
            session['whatsapp_link'] = whatsapp_link
            return redirect(url_for('messaging.whatsapp_confirm'))
        else:
            flash('فشل إنشاء رابط الواتساب', 'danger')
            return redirect(url_for('financial.view_receipt', receipt_id=receipt_id))
    
    templates = WhatsAppTemplate.query.filter_by(is_active=True).all()
    return render_template('messaging/send_whatsapp.html', 
                          document=receipt, 
                          document_type='receipt',
                          templates=templates,
                          recipient_phone=receipt.client_phone if hasattr(receipt, 'client_phone') else '')

# صفحة تأكيد إرسال الواتساب
@messaging.route('/messages/whatsapp-confirm')
@login_required
def whatsapp_confirm():
    whatsapp_link = session.get('whatsapp_link')
    if not whatsapp_link:
        flash('لم يتم العثور على رابط الواتساب', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('messaging/whatsapp_confirm.html', whatsapp_link=whatsapp_link)

# واجهة برمجة التطبيقات للرسائل
@messaging.route('/api/messages/logs', methods=['GET'])
@login_required
def api_message_logs():
    logs = MessageLog.query.order_by(MessageLog.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])
