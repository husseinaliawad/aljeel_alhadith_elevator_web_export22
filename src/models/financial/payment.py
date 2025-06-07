"""
نموذج سندات الصرف
"""
from datetime import datetime
from src.models.db import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), nullable=False, unique=True)
    date = db.Column(db.Date, nullable=False)
    recipient_id = db.Column(db.Integer)
    recipient_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # نقداً، شيك، تحويل بنكي، إلخ
    reference_number = db.Column(db.String(100))  # رقم الشيك أو التحويل
    notes = db.Column(db.Text)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))  # رقم العقد المرتبط (إن وجد)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance_requests.id'))  # رقم طلب الصيانة المرتبط (إن وجد)
    created_by = db.Column(db.String(100), nullable=False)  # اسم الموظف الذي أنشأ السند
    status = db.Column(db.String(20), nullable=False)  # مكتمل، ملغي
    category = db.Column(db.String(50))  # تصنيف المصروف (رواتب، قطع غيار، مصاريف تشغيلية، إلخ)
    
    # العلاقات
    contract = db.relationship('Contract', backref=db.backref('payments', lazy=True))
    maintenance_request = db.relationship('MaintenanceRequest', backref=db.backref('payments', lazy=True))
    
    def __init__(self, payment_number=None, date=None, recipient_id=None, recipient_name=None, 
                 amount=None, payment_method=None, reference_number=None, notes=None, 
                 contract_id=None, maintenance_id=None, created_by=None, status=None, category=None):
        self.payment_number = payment_number
        self.date = date
        self.recipient_id = recipient_id
        self.recipient_name = recipient_name
        self.amount = amount
        self.payment_method = payment_method
        self.reference_number = reference_number
        self.notes = notes
        self.contract_id = contract_id
        self.maintenance_id = maintenance_id
        self.created_by = created_by
        self.status = status
        self.category = category
    
    def save(self):
        """حفظ بيانات سند الصرف في قاعدة البيانات"""
        db.session.add(self)
        db.session.commit()
        return self.id
    
    def delete(self):
        """حذف سند صرف من قاعدة البيانات"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    def cancel(self):
        """إلغاء سند صرف"""
        self.status = "ملغي"
        db.session.commit()
        return True
    
    @staticmethod
    def get_by_id(payment_id):
        """استرجاع بيانات سند الصرف بواسطة المعرف"""
        return Payment.query.get(payment_id)
    
    @staticmethod
    def get_all():
        """استرجاع جميع سندات الصرف"""
        return Payment.query.order_by(Payment.date.desc()).all()
    
    @staticmethod
    def get_by_recipient_id(recipient_id):
        """استرجاع سندات الصرف لمستلم معين"""
        return Payment.query.filter_by(recipient_id=recipient_id).order_by(Payment.date.desc()).all()
    
    @staticmethod
    def get_by_contract_id(contract_id):
        """استرجاع سندات الصرف لعقد معين"""
        return Payment.query.filter_by(contract_id=contract_id).order_by(Payment.date.desc()).all()
    
    @staticmethod
    def get_by_date_range(start_date, end_date):
        """استرجاع سندات الصرف ضمن فترة زمنية محددة"""
        return Payment.query.filter(Payment.date.between(start_date, end_date)).order_by(Payment.date).all()
    
    @staticmethod
    def get_by_category(category):
        """استرجاع سندات الصرف حسب التصنيف"""
        return Payment.query.filter_by(category=category).order_by(Payment.date.desc()).all()
    
    @staticmethod
    def generate_payment_number():
        """توليد رقم سند صرف فريد"""
        year = datetime.now().year
        month = datetime.now().month
        
        count = Payment.query.filter(
            Payment.payment_number.like(f'PAY-{year}{month:02d}-%')
        ).count() + 1
        
        return f'PAY-{year}{month:02d}-{count:04d}'
