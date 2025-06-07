"""
نموذج الصيانة الدورية لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db

class ScheduledMaintenance(db.Model):
    """فئة تمثل صيانة دورية مجدولة"""
    
    __tablename__ = 'scheduled_maintenances'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    elevator_id = db.Column(db.Integer, db.ForeignKey('elevators.id'), nullable=False)
    scheduled_date = db.Column(db.String(20), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="مجدولة")
    completion_date = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, elevator_id=None, scheduled_date=None, 
                 maintenance_type=None, status="مجدولة", 
                 completion_date=None, notes=None):
        """
        تهيئة صيانة دورية جديدة
        
        المعلمات:
            elevator_id (int): رقم المصعد
            scheduled_date (str): التاريخ المجدول
            maintenance_type (str): نوع الصيانة (دورية، وقائية، شاملة)
            status (str): الحالة (مجدولة، مكتملة، مؤجلة، ملغاة)
            completion_date (str): تاريخ الإكمال
            notes (str): ملاحظات
        """
        self.elevator_id = elevator_id
        self.scheduled_date = scheduled_date
        self.maintenance_type = maintenance_type
        self.status = status
        self.completion_date = completion_date
        self.notes = notes
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل الصيانة الدورية
        """
        return {
            'id': self.id,
            'elevator_id': self.elevator_id,
            'scheduled_date': self.scheduled_date,
            'maintenance_type': self.maintenance_type,
            'status': self.status,
            'completion_date': self.completion_date,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
