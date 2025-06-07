"""
نموذج شهادات السلامة
"""
from datetime import datetime
from src.models.db import db

class SafetyCertificate(db.Model):
    __tablename__ = 'safety_certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    elevator_id = db.Column(db.Integer, db.ForeignKey('elevators.id'), nullable=False)
    certificate_number = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    issuing_authority = db.Column(db.String(100), nullable=False)  # الجهة المصدرة للشهادة
    certificate_type = db.Column(db.String(50), nullable=False)  # نوع الشهادة (سلامة عامة، مطابقة، إلخ)
    status = db.Column(db.String(20), nullable=False)  # سارية، منتهية، ملغاة
    notes = db.Column(db.Text)
    issued_by = db.Column(db.String(100), nullable=False)  # اسم المهندس أو المفتش المصدر
    
    # العلاقات
    elevator = db.relationship('Elevator', backref=db.backref('certificates', lazy=True))
    
    def __init__(self, elevator_id=None, certificate_number=None, issue_date=None, 
                 expiry_date=None, issuing_authority=None, certificate_type=None, 
                 status=None, notes=None, issued_by=None):
        self.elevator_id = elevator_id
        self.certificate_number = certificate_number
        self.issue_date = issue_date
        self.expiry_date = expiry_date
        self.issuing_authority = issuing_authority
        self.certificate_type = certificate_type
        self.status = status
        self.notes = notes
        self.issued_by = issued_by
    
    def save(self):
        """حفظ بيانات شهادة السلامة في قاعدة البيانات"""
        db.session.add(self)
        db.session.commit()
        return self.id
    
    def delete(self):
        """حذف شهادة سلامة من قاعدة البيانات"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    @staticmethod
    def get_by_id(certificate_id):
        """استرجاع بيانات شهادة السلامة بواسطة المعرف"""
        return SafetyCertificate.query.get(certificate_id)
    
    @staticmethod
    def get_all():
        """استرجاع جميع شهادات السلامة"""
        return SafetyCertificate.query.order_by(SafetyCertificate.expiry_date).all()
    
    @staticmethod
    def get_by_elevator_id(elevator_id):
        """استرجاع شهادات السلامة لمصعد معين"""
        return SafetyCertificate.query.filter_by(elevator_id=elevator_id).order_by(SafetyCertificate.expiry_date).all()
    
    @staticmethod
    def get_expiring_certificates(days=30):
        """استرجاع شهادات السلامة التي ستنتهي قريباً"""
        today = datetime.now().date()
        future_date = today + datetime.timedelta(days=days)
        return SafetyCertificate.query.filter(
            SafetyCertificate.status == 'سارية',
            SafetyCertificate.expiry_date <= future_date,
            SafetyCertificate.expiry_date >= today
        ).order_by(SafetyCertificate.expiry_date).all()
    
    @staticmethod
    def update_expired_certificates():
        """تحديث حالة الشهادات المنتهية"""
        today = datetime.now().date()
        expired_certs = SafetyCertificate.query.filter(
            SafetyCertificate.status == 'سارية',
            SafetyCertificate.expiry_date < today
        ).all()
        
        for cert in expired_certs:
            cert.status = 'منتهية'
        
        db.session.commit()
        return len(expired_certs)
    
    @staticmethod
    def generate_certificate_number(elevator_id):
        """توليد رقم شهادة فريد"""
        year = datetime.now().year
        count = SafetyCertificate.query.filter(
            SafetyCertificate.elevator_id == elevator_id,
            db.extract('year', SafetyCertificate.issue_date) == year
        ).count() + 1
        
        return f'CERT-{year}-{elevator_id:04d}-{count:03d}'
