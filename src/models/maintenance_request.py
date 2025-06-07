"""
نموذج طلبات الصيانة لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db

class MaintenanceRequest(db.Model):
    """فئة تمثل طلب صيانة"""
    
    __tablename__ = 'maintenance_requests'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_date = db.Column(db.String(20), nullable=False)
    building_name = db.Column(db.String(100), nullable=False)
    elevator_id = db.Column(db.Integer, db.ForeignKey('elevators.id'), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="جديد")
    completion_date = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات مع الجداول الأخرى
    part_usages = db.relationship('PartUsage', backref='maintenance_request', lazy=True)
    
    def __init__(self, request_date=None, building_name=None, elevator_id=None, 
                 issue_description=None, priority=None, status="جديد", 
                 completion_date=None, notes=None):
        """
        تهيئة طلب صيانة جديد
        
        المعلمات:
            request_date (str): تاريخ تقديم الطلب
            building_name (str): اسم المبنى
            elevator_id (int): رقم تعريف المصعد
            issue_description (str): وصف المشكلة
            priority (str): الأولوية (عالية، متوسطة، منخفضة)
            status (str): حالة الطلب (جديد، قيد المعالجة، مكتمل، ملغي)
            completion_date (str): تاريخ إكمال الصيانة
            notes (str): ملاحظات إضافية
        """
        self.request_date = request_date
        self.building_name = building_name
        self.elevator_id = elevator_id
        self.issue_description = issue_description
        self.priority = priority
        self.status = status
        self.completion_date = completion_date
        self.notes = notes
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل طلب الصيانة
        """
        return {
            'id': self.id,
            'request_date': self.request_date,
            'building_name': self.building_name,
            'elevator_id': self.elevator_id,
            'issue_description': self.issue_description,
            'priority': self.priority,
            'status': self.status,
            'completion_date': self.completion_date,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
