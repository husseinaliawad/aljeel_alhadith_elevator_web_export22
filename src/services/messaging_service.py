"""
خدمات إرسال الرسائل عبر البريد الإلكتروني والواتساب
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import urllib.parse
from src.models.messaging import MessageLog, EmailTemplate, WhatsAppTemplate
from src.models.db import db
from flask import current_app, render_template

class MessagingService:
    """خدمة إرسال الرسائل عبر البريد الإلكتروني والواتساب"""
    
    @staticmethod
    def send_email(recipient_email, subject, body, attachment_path=None, document_type=None, document_id=None):
        """
        إرسال بريد إلكتروني
        
        Args:
            recipient_email: البريد الإلكتروني للمستلم
            subject: موضوع البريد الإلكتروني
            body: نص البريد الإلكتروني
            attachment_path: مسار الملف المرفق (اختياري)
            document_type: نوع المستند (اختياري)
            document_id: معرف المستند (اختياري)
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        try:
            # إنشاء سجل رسالة جديد
            message_log = MessageLog(
                document_type=document_type or 'email',
                document_id=document_id or 0,
                recipient=recipient_email,
                channel='email',
                status='pending'
            )
            db.session.add(message_log)
            db.session.commit()
            
            # إعداد البريد الإلكتروني
            msg = MIMEMultipart()
            msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER', 'info@aljeelalhadith.com')
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # إضافة نص البريد الإلكتروني
            msg.attach(MIMEText(body, 'html'))
            
            # إضافة المرفق إذا كان موجوداً
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as file:
                    attachment = MIMEApplication(file.read(), _subtype="pdf")
                    attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                    msg.attach(attachment)
            
            # إرسال البريد الإلكتروني
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME', '')
            smtp_password = current_app.config.get('MAIL_PASSWORD', '')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            # تحديث سجل الرسالة
            message_log.status = 'sent'
            message_log.sent_at = datetime.utcnow()
            db.session.commit()
            
            return True
        
        except Exception as e:
            # تسجيل الخطأ
            if message_log:
                message_log.status = 'failed'
                message_log.error_message = str(e)
                db.session.commit()
            
            current_app.logger.error(f"فشل إرسال البريد الإلكتروني: {str(e)}")
            return False
    
    @staticmethod
    def generate_whatsapp_link(phone_number, message, document_url=None):
        """
        إنشاء رابط واتساب
        
        Args:
            phone_number: رقم الهاتف بدون الرمز + (مثال: 966512345678)
            message: نص الرسالة
            document_url: رابط المستند (اختياري)
        
        Returns:
            str: رابط واتساب
        """
        # إضافة رابط المستند إلى الرسالة إذا كان موجوداً
        if document_url:
            message += f"\n\nيمكنك الاطلاع على المستند من خلال الرابط التالي:\n{document_url}"
        
        # ترميز الرسالة للاستخدام في URL
        encoded_message = urllib.parse.quote(message)
        
        # إنشاء رابط واتساب
        whatsapp_link = f"https://wa.me/{phone_number}?text={encoded_message}"
        
        return whatsapp_link
    
    @staticmethod
    def send_document_by_email(document_type, document_id, recipient_email, template_name=None):
        """
        إرسال مستند عبر البريد الإلكتروني
        
        Args:
            document_type: نوع المستند (contract, quote, receipt)
            document_id: معرف المستند
            recipient_email: البريد الإلكتروني للمستلم
            template_name: اسم قالب البريد الإلكتروني (اختياري)
        
        Returns:
            bool: نجاح أو فشل الإرسال
        """
        try:
            # الحصول على المستند
            document = None
            document_name = ""
            attachment_path = None
            
            if document_type == 'contract':
                from src.models.contract import Contract
                document = Contract.query.get(document_id)
                document_name = f"عقد رقم {document.contract_number}"
                # إنشاء ملف PDF للعقد
                from src.services.pdf_service import generate_contract_pdf
                attachment_path = generate_contract_pdf(document)
            
            elif document_type == 'quote':
                from src.models.quote import Quote
                document = Quote.query.get(document_id)
                document_name = f"عرض سعر رقم {document.quote_number}"
                # إنشاء ملف PDF لعرض السعر
                from src.services.pdf_service import generate_quote_pdf
                attachment_path = generate_quote_pdf(document)
            
            elif document_type == 'receipt':
                from src.models.financial.receipt import Receipt
                document = Receipt.query.get(document_id)
                document_name = f"إيصال رقم {document.receipt_number}"
                # إنشاء ملف PDF للإيصال
                from src.services.pdf_service import generate_receipt_pdf
                attachment_path = generate_receipt_pdf(document)
            
            if not document:
                raise ValueError(f"لم يتم العثور على المستند: {document_type} بالمعرف {document_id}")
            
            # الحصول على قالب البريد الإلكتروني
            template = None
            if template_name:
                template = EmailTemplate.query.filter_by(name=template_name, is_active=True).first()
            
            if not template:
                # استخدام القالب الافتراضي
                template = EmailTemplate.query.filter_by(name=f"default_{document_type}", is_active=True).first()
            
            if not template:
                # إنشاء موضوع ونص افتراضي
                subject = f"الجيل الحديث للأمن والمصاعد - {document_name}"
                body = render_template('emails/default_document.html', 
                                      document_type=document_type,
                                      document=document,
                                      document_name=document_name)
            else:
                # استخدام القالب المخصص
                subject = template.subject.replace('{{document_name}}', document_name)
                body = template.body.replace('{{document_name}}', document_name)
            
            # إرسال البريد الإلكتروني
            return MessagingService.send_email(
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                attachment_path=attachment_path,
                document_type=document_type,
                document_id=document_id
            )
        
        except Exception as e:
            current_app.logger.error(f"فشل إرسال المستند عبر البريد الإلكتروني: {str(e)}")
            return False
    
    @staticmethod
    def get_document_whatsapp_link(document_type, document_id, phone_number, template_name=None):
        """
        الحصول على رابط واتساب لإرسال مستند
        
        Args:
            document_type: نوع المستند (contract, quote, receipt)
            document_id: معرف المستند
            phone_number: رقم الهاتف بدون الرمز + (مثال: 966512345678)
            template_name: اسم قالب الواتساب (اختياري)
        
        Returns:
            str: رابط واتساب
        """
        try:
            # الحصول على المستند
            document = None
            document_name = ""
            
            if document_type == 'contract':
                from src.models.contract import Contract
                document = Contract.query.get(document_id)
                document_name = f"عقد رقم {document.contract_number}"
            
            elif document_type == 'quote':
                from src.models.quote import Quote
                document = Quote.query.get(document_id)
                document_name = f"عرض سعر رقم {document.quote_number}"
            
            elif document_type == 'receipt':
                from src.models.financial.receipt import Receipt
                document = Receipt.query.get(document_id)
                document_name = f"إيصال رقم {document.receipt_number}"
            
            if not document:
                raise ValueError(f"لم يتم العثور على المستند: {document_type} بالمعرف {document_id}")
            
            # الحصول على قالب الواتساب
            template = None
            if template_name:
                template = WhatsAppTemplate.query.filter_by(name=template_name, is_active=True).first()
            
            if not template:
                # استخدام القالب الافتراضي
                template = WhatsAppTemplate.query.filter_by(name=f"default_{document_type}", is_active=True).first()
            
            # إنشاء رابط للمستند (في الإنتاج، يجب أن يكون هذا رابطًا فعليًا للمستند)
            document_url = f"https://aljeelalhadith.com/documents/{document_type}/{document_id}"
            
            if not template:
                # إنشاء رسالة افتراضية
                message = f"مرحباً،\n\nنرسل لكم {document_name} من شركة الجيل الحديث للأمن والمصاعد."
            else:
                # استخدام القالب المخصص
                message = template.message.replace('{{document_name}}', document_name)
            
            # إنشاء سجل رسالة جديد
            message_log = MessageLog(
                document_type=document_type,
                document_id=document_id,
                recipient=phone_number,
                channel='whatsapp',
                status='generated'
            )
            db.session.add(message_log)
            db.session.commit()
            
            # إنشاء رابط واتساب
            return MessagingService.generate_whatsapp_link(
                phone_number=phone_number,
                message=message,
                document_url=document_url
            )
        
        except Exception as e:
            current_app.logger.error(f"فشل إنشاء رابط واتساب للمستند: {str(e)}")
            return None
