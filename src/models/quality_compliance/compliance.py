"""
نموذج متابعة الامتثال للوائح والمعايير
"""
from datetime import datetime
from src.models.db import db

class ComplianceStandard(db.Model):
    __tablename__ = 'compliance_standards'
    
    id = db.Column(db.Integer, primary_key=True)
    standard_name = db.Column(db.String(100), nullable=False)  # اسم المعيار أو اللائحة
    standard_code = db.Column(db.String(50), nullable=False)  # رمز المعيار
    issuing_body = db.Column(db.String(100), nullable=False)  # الجهة المصدرة للمعيار
    description = db.Column(db.Text)  # وصف المعيار
    requirements = db.Column(db.Text)  # متطلبات الامتثال
    effective_date = db.Column(db.Date, nullable=False)  # تاريخ سريان المعيار
    status = db.Column(db.String(20), nullable=False)  # حالة المعيار (ساري، ملغي، محدث)
    
    # العلاقات
    elevator_compliances = db.relationship('ElevatorCompliance', backref='standard', lazy=True)
    
    def __init__(self, standard_name=None, standard_code=None, issuing_body=None, 
                 description=None, requirements=None, effective_date=None, status=None):
        self.standard_name = standard_name
        self.standard_code = standard_code
        self.issuing_body = issuing_body
        self.description = description
        self.requirements = requirements
        self.effective_date = effective_date
        self.status = status
    
    def save(self):
        """حفظ بيانات معيار الامتثال في قاعدة البيانات"""
        db.session.add(self)
        db.session.commit()
        return self.id
    
    def delete(self):
        """حذف معيار امتثال من قاعدة البيانات"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    @staticmethod
    def get_by_id(standard_id):
        """استرجاع بيانات معيار الامتثال بواسطة المعرف"""
        return ComplianceStandard.query.get(standard_id)
    
    @staticmethod
    def get_all():
        """استرجاع جميع معايير الامتثال"""
        return ComplianceStandard.query.order_by(ComplianceStandard.effective_date.desc()).all()
    
    @staticmethod
    def get_active_standards():
        """استرجاع معايير الامتثال السارية"""
        return ComplianceStandard.query.filter_by(status='ساري').order_by(ComplianceStandard.effective_date.desc()).all()


class ElevatorCompliance(db.Model):
    __tablename__ = 'elevator_compliance'
    
    id = db.Column(db.Integer, primary_key=True)
    elevator_id = db.Column(db.Integer, db.ForeignKey('elevators.id'), nullable=False)
    standard_id = db.Column(db.Integer, db.ForeignKey('compliance_standards.id'), nullable=False)
    compliance_status = db.Column(db.String(50), nullable=False)  # ممتثل، غير ممتثل، ممتثل جزئياً
    last_check_date = db.Column(db.Date, nullable=False)
    next_check_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    checked_by = db.Column(db.String(100), nullable=False)  # اسم المهندس أو المفتش
    
    # العلاقات
    elevator = db.relationship('Elevator', backref=db.backref('compliances', lazy=True))
    
    def __init__(self, elevator_id=None, standard_id=None, compliance_status=None, 
                 last_check_date=None, next_check_date=None, notes=None, checked_by=None):
        self.elevator_id = elevator_id
        self.standard_id = standard_id
        self.compliance_status = compliance_status
        self.last_check_date = last_check_date
        self.next_check_date = next_check_date
        self.notes = notes
        self.checked_by = checked_by
    
    def save(self):
        """حفظ بيانات امتثال المصعد في قاعدة البيانات"""
        db.session.add(self)
        db.session.commit()
        return self.id
    
    def delete(self):
        """حذف سجل امتثال من قاعدة البيانات"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    @staticmethod
    def get_by_id(compliance_id):
        """استرجاع بيانات امتثال المصعد بواسطة المعرف"""
        return ElevatorCompliance.query.get(compliance_id)
    
    @staticmethod
    def get_by_elevator_id(elevator_id):
        """استرجاع بيانات امتثال مصعد معين"""
        return db.session.query(
            ElevatorCompliance, 
            ComplianceStandard.standard_name, 
            ComplianceStandard.standard_code
        ).join(
            ComplianceStandard, 
            ElevatorCompliance.standard_id == ComplianceStandard.id
        ).filter(
            ElevatorCompliance.elevator_id == elevator_id
        ).order_by(
            ElevatorCompliance.next_check_date
        ).all()
    
    @staticmethod
    def get_upcoming_checks(days=30):
        """استرجاع فحوصات الامتثال القادمة"""
        today = datetime.now().date()
        future_date = today + datetime.timedelta(days=days)
        
        return db.session.query(
            ElevatorCompliance,
            ComplianceStandard.standard_name,
            ComplianceStandard.standard_code,
            db.literal_column('elevators.name').label('elevator_name'),
            db.literal_column('elevators.location').label('elevator_location')
        ).join(
            ComplianceStandard,
            ElevatorCompliance.standard_id == ComplianceStandard.id
        ).join(
            db.literal_column('elevators'),
            ElevatorCompliance.elevator_id == db.literal_column('elevators.id')
        ).filter(
            ElevatorCompliance.next_check_date.isnot(None),
            ElevatorCompliance.next_check_date <= future_date,
            ElevatorCompliance.next_check_date >= today
        ).order_by(
            ElevatorCompliance.next_check_date
        ).all()
    
    @staticmethod
    def get_non_compliant_elevators():
        """استرجاع المصاعد غير الممتثلة للمعايير"""
        return db.session.query(
            ElevatorCompliance,
            ComplianceStandard.standard_name,
            ComplianceStandard.standard_code,
            db.literal_column('elevators.name').label('elevator_name'),
            db.literal_column('elevators.location').label('elevator_location')
        ).join(
            ComplianceStandard,
            ElevatorCompliance.standard_id == ComplianceStandard.id
        ).join(
            db.literal_column('elevators'),
            ElevatorCompliance.elevator_id == db.literal_column('elevators.id')
        ).filter(
            ElevatorCompliance.compliance_status == 'غير ممتثل'
        ).order_by(
            ElevatorCompliance.last_check_date.desc()
        ).all()
