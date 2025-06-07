"""
نموذج استخدام قطع الغيار لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db

class PartUsage(db.Model):
    """فئة تمثل استخدام قطعة غيار"""
    
    __tablename__ = 'part_usages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('maintenance_requests.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity_used = db.Column(db.Integer, default=0)
    usage_date = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, request_id=None, part_id=None, 
                 quantity_used=0, usage_date=None):
        """
        تهيئة استخدام قطعة غيار جديد
        
        المعلمات:
            request_id (int): رقم طلب الصيانة
            part_id (int): رقم قطعة الغيار
            quantity_used (int): الكمية المستخدمة
            usage_date (str): تاريخ الاستخدام
        """
        self.request_id = request_id
        self.part_id = part_id
        self.quantity_used = quantity_used
        self.usage_date = usage_date
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل استخدام قطعة الغيار
        """
        return {
            'id': self.id,
            'request_id': self.request_id,
            'part_id': self.part_id,
            'quantity_used': self.quantity_used,
            'usage_date': self.usage_date,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
