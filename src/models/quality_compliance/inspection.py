"""
نموذج توثيق عمليات الفحص والصيانة
"""
from datetime import datetime
from src.models.db import db

class Inspection(db.Model):
    __tablename__ = 'inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    elevator_id = db.Column(db.Integer, db.ForeignKey('elevators.id'), nullable=False)
    inspector_name = db.Column(db.String(100), nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)
    inspection_type = db.Column(db.String(50), nullable=False)  # دوري، طارئ، شهادة سلامة
    status = db.Column(db.String(50), nullable=False)  # مكتمل، معلق، فشل
    notes = db.Column(db.Text)
    compliance_status = db.Column(db.String(50), nullable=False)  # ممتثل، غير ممتثل، ممتثل جزئياً
    next_inspection_date = db.Column(db.Date)
    certificate_id = db.Column(db.Integer, db.ForeignKey('safety_certificates.id'))
    
    # العلاقات
    elevator = db.relationship('Elevator', backref=db.backref('inspections', lazy=True))
    certificate = db.relationship('SafetyCertificate', backref=db.backref('inspections', lazy=True))
    
    def __init__(self, elevator_id=None, inspector_name=None, inspection_date=None, 
                 inspection_type=None, status=None, notes=None, compliance_status=None, 
                 next_inspection_date=None, certificate_id=None):
        self.elevator_id = elevator_id
        self.inspector_name = inspector_name
        self.inspection_date = inspection_date
        self.inspection_type = inspection_type
        self.status = status
        self.notes = notes
        self.compliance_status = compliance_status
        self.next_inspection_date = next_inspection_date
        self.certificate_id = certificate_id
    
    def save(self):
        """حفظ بيانات الفحص في قاعدة البيانات"""
        db.session.add(self)
        db.session.commit()
        return self.id
    
    def delete(self):
        """حذف عملية فحص من قاعدة البيانات"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    @staticmethod
    def get_by_id(inspection_id):
        """استرجاع بيانات الفحص بواسطة المعرف"""
        return Inspection.query.get(inspection_id)
    
    @staticmethod
    def get_all():
        """استرجاع جميع عمليات الفحص"""
        return Inspection.query.order_by(Inspection.inspection_date.desc()).all()
    
    @staticmethod
    def get_by_elevator_id(elevator_id):
        """استرجاع عمليات الفحص لمصعد معين"""
        return Inspection.query.filter_by(elevator_id=elevator_id).order_by(Inspection.inspection_date.desc()).all()
    
    @staticmethod
    def get_upcoming_inspections(days=30):
        """استرجاع عمليات الفحص القادمة خلال فترة محددة"""
        today = datetime.now().date()
        future_date = today + datetime.timedelta(days=days)
        return Inspection.query.filter(
            Inspection.next_inspection_date.isnot(None),
            Inspection.next_inspection_date <= future_date,
            Inspection.next_inspection_date >= today
        ).order_by(Inspection.next_inspection_date).all()
