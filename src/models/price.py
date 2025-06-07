"""
نموذج الأسعار لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db

class Price(db.Model):
    """نموذج الأسعار"""
    
    __tablename__ = 'prices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, service_name=None, description=None, price=0.0, unit=None, category=None, notes=None):
        """
        تهيئة كائن السعر
        
        المعلمات:
            service_name (str): اسم الخدمة
            description (str): وصف الخدمة
            price (float): سعر الخدمة
            unit (str): وحدة القياس (مثل: ساعة، قطعة، شهر)
            category (str): فئة الخدمة (مثل: صيانة، قطع غيار، تركيب)
            notes (str): ملاحظات إضافية (اختياري)
        """
        self.service_name = service_name
        self.description = description
        self.price = price
        self.unit = unit
        self.category = category
        self.notes = notes
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل السعر
        """
        return {
            'id': self.id,
            'service_name': self.service_name,
            'description': self.description,
            'price': self.price,
            'unit': self.unit,
            'category': self.category,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
