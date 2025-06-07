"""
نموذج عروض الأسعار لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db
import json

class Quote(db.Model):
    """نموذج عروض الأسعار"""
    
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quote_number = db.Column(db.String(50), nullable=False, unique=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_contact = db.Column(db.String(100), nullable=True)
    issue_date = db.Column(db.String(20), nullable=False)
    valid_until = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="معلق")  # معلق، مقبول، مرفوض، منتهي
    items = db.Column(db.Text, nullable=True)  # سيتم تخزينها كسلسلة JSON
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, quote_number=None, client_name=None, client_contact=None, 
                 issue_date=None, valid_until=None, total_amount=0.0, 
                 status="معلق", items=None, notes=None):
        """
        تهيئة كائن عرض السعر
        
        المعلمات:
            quote_number (str): رقم عرض السعر
            client_name (str): اسم العميل
            client_contact (str): معلومات الاتصال بالعميل
            issue_date (str): تاريخ إصدار العرض
            valid_until (str): تاريخ انتهاء صلاحية العرض
            total_amount (float): المبلغ الإجمالي
            status (str): حالة العرض (معلق، مقبول، مرفوض، منتهي)
            items (list): قائمة بنود العرض
            notes (str): ملاحظات إضافية
        """
        self.quote_number = quote_number
        self.client_name = client_name
        self.client_contact = client_contact
        self.issue_date = issue_date
        self.valid_until = valid_until
        self.total_amount = total_amount
        self.status = status
        self.items = json.dumps(items) if items else json.dumps([])
        self.notes = notes
    
    def get_items(self):
        """
        الحصول على قائمة بنود العرض
        
        العائد:
            list: قائمة بنود العرض
        """
        return json.loads(self.items) if self.items else []
    
    def set_items(self, items):
        """
        تعيين قائمة بنود العرض
        
        المعلمات:
            items (list): قائمة بنود العرض
        """
        self.items = json.dumps(items)
        
    def is_valid(self):
        """
        التحقق مما إذا كان العرض ساري المفعول
        
        العائد:
            bool: True إذا كان العرض ساري المفعول، False خلاف ذلك
        """
        if self.status != "معلق":
            return False
            
        today = datetime.now().strftime("%Y-%m-%d")
        return today <= self.valid_until
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل عرض السعر
        """
        return {
            'id': self.id,
            'quote_number': self.quote_number,
            'client_name': self.client_name,
            'client_contact': self.client_contact,
            'issue_date': self.issue_date,
            'valid_until': self.valid_until,
            'total_amount': self.total_amount,
            'status': self.status,
            'items': self.get_items(),
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
