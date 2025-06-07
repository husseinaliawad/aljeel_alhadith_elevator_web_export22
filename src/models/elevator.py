"""
نموذج المصاعد لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db

class Elevator(db.Model):
    """فئة تمثل مصعد"""
    
    __tablename__ = 'elevators'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    installation_date = db.Column(db.String(20), nullable=True)
    last_maintenance_date = db.Column(db.String(20), nullable=True)
    maintenance_interval = db.Column(db.Integer, default=90)
    status = db.Column(db.String(20), default="يعمل")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات مع الجداول الأخرى
    maintenance_requests = db.relationship('MaintenanceRequest', backref='elevator', lazy=True)
    scheduled_maintenances = db.relationship('ScheduledMaintenance', backref='elevator', lazy=True)
    
    def __init__(self, building_name=None, model=None, 
                 installation_date=None, last_maintenance_date=None, 
                 maintenance_interval=90, status="يعمل"):
        """
        تهيئة مصعد جديد
        
        المعلمات:
            building_name (str): اسم المبنى
            model (str): طراز المصعد
            installation_date (str): تاريخ التركيب
            last_maintenance_date (str): تاريخ آخر صيانة
            maintenance_interval (int): الفترة الزمنية بين الصيانات الدورية (بالأيام)
            status (str): حالة المصعد (يعمل، متوقف، قيد الصيانة)
        """
        self.building_name = building_name
        self.model = model
        self.installation_date = installation_date
        self.last_maintenance_date = last_maintenance_date
        self.maintenance_interval = maintenance_interval
        self.status = status
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل المصعد
        """
        return {
            'id': self.id,
            'building_name': self.building_name,
            'model': self.model,
            'installation_date': self.installation_date,
            'last_maintenance_date': self.last_maintenance_date,
            'maintenance_interval': self.maintenance_interval,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
