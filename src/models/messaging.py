"""
نموذج إرسال الرسائل عبر البريد الإلكتروني والواتساب
"""
from datetime import datetime
from src.models.db import db

class MessageLog(db.Model):
    """نموذج لتسجيل الرسائل المرسلة"""
    __tablename__ = 'message_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.String(50), nullable=False)  # نوع المستند (عقد، عرض سعر، سند)
    document_id = db.Column(db.Integer, nullable=False)  # معرف المستند
    recipient = db.Column(db.String(255), nullable=False)  # المستلم (بريد إلكتروني أو رقم هاتف)
    channel = db.Column(db.String(20), nullable=False)  # قناة الإرسال (بريد إلكتروني، واتساب)
    status = db.Column(db.String(20), nullable=False, default='pending')  # حالة الإرسال (معلق، تم، فشل)
    error_message = db.Column(db.Text, nullable=True)  # رسالة الخطأ في حالة الفشل
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<MessageLog {self.id}: {self.document_type} to {self.recipient} via {self.channel}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_type': self.document_type,
            'document_id': self.document_id,
            'recipient': self.recipient,
            'channel': self.channel,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'sent_at': self.sent_at.strftime('%Y-%m-%d %H:%M:%S') if self.sent_at else None
        }


class EmailTemplate(db.Model):
    """نموذج لقوالب البريد الإلكتروني"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # اسم القالب
    subject = db.Column(db.String(255), nullable=False)  # موضوع البريد الإلكتروني
    body = db.Column(db.Text, nullable=False)  # نص البريد الإلكتروني
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class WhatsAppTemplate(db.Model):
    """نموذج لقوالب رسائل الواتساب"""
    __tablename__ = 'whatsapp_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # اسم القالب
    message = db.Column(db.Text, nullable=False)  # نص الرسالة
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<WhatsAppTemplate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'message': self.message,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
