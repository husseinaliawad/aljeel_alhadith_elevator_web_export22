"""
نموذج قطع الغيار لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db

class Part(db.Model):
    """فئة تمثل قطعة غيار"""
    
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=5)
    last_restock_date = db.Column(db.String(20), nullable=True)
    price = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات مع الجداول الأخرى
    part_usages = db.relationship('PartUsage', backref='part', lazy=True)
    
    def __init__(self, name=None, description=None, 
                 quantity=0, min_quantity=5, last_restock_date=None, price=0):
        """
        تهيئة قطعة غيار جديدة
        
        المعلمات:
            name (str): اسم قطعة الغيار
            description (str): وصف قطعة الغيار
            quantity (int): الكمية المتوفرة
            min_quantity (int): الحد الأدنى للكمية
            last_restock_date (str): تاريخ آخر إعادة تخزين
            price (float): السعر
        """
        self.name = name
        self.description = description
        self.quantity = quantity
        self.min_quantity = min_quantity
        self.last_restock_date = last_restock_date
        self.price = price
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل قطعة الغيار
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'min_quantity': self.min_quantity,
            'last_restock_date': self.last_restock_date,
            'price': self.price,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
    def is_low_stock(self):
        """
        التحقق مما إذا كانت الكمية أقل من الحد الأدنى
        
        العائد:
            bool: True إذا كانت الكمية أقل من الحد الأدنى
        """
        return self.quantity < self.min_quantity
