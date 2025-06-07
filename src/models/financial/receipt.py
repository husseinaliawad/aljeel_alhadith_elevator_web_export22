"""
نموذج سندات القبض
"""
from datetime import datetime
from src.models.db import db

class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(50), nullable=False, unique=True)
    date = db.Column(db.Date, nullable=False)
    # تم إزالة العلاقة مع جدول العملاء غير الموجود
    # client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    client_id = db.Column(db.Integer)  # تخزين معرف العميل بدون علاقة خارجية
    client_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # نقداً، شيك، تحويل بنكي، إلخ
    reference_number = db.Column(db.String(100))  # رقم الشيك أو التحويل
    notes = db.Column(db.Text)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))  # رقم العقد المرتبط (إن وجد)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))  # رقم عرض السعر المرتبط (إن وجد)
    created_by = db.Column(db.String(100), nullable=False)  # اسم الموظف الذي أنشأ السند
    status = db.Column(db.String(20), nullable=False)  # مكتمل، ملغي
    
    # العلاقات
    contract = db.relationship('Contract', backref=db.backref('receipts', lazy=True))
    quote = db.relationship('Quote', backref=db.backref('receipts', lazy=True))
    
    def __init__(self, receipt_number=None, date=None, client_id=None, client_name=None, 
                 amount=None, payment_method=None, reference_number=None, notes=None, 
                 contract_id=None, quote_id=None, created_by=None, status=None):
        self.receipt_number = receipt_number
        self.date = date
        self.client_id = client_id
        self.client_name = client_name
        self.amount = amount
        self.payment_method = payment_method
        self.reference_number = reference_number
        self.notes = notes
        self.contract_id = contract_id
        self.quote_id = quote_id
        self.created_by = created_by
        self.status = status
    
    def save(self):
        """حفظ بيانات سند القبض في قاعدة البيانات"""
        db.session.add(self)
        db.session.commit()
        return self.id
    
    def delete(self):
        """حذف سند قبض من قاعدة البيانات"""
        db.session.delete(self)
        db.session.commit()
        return True
    
    def cancel(self):
        """إلغاء سند قبض"""
        self.status = "ملغي"
        db.session.commit()
        return True
    
    @staticmethod
    def get_by_id(receipt_id):
        """استرجاع بيانات سند القبض بواسطة المعرف"""
        return Receipt.query.get(receipt_id)
    
    @staticmethod
    def get_all():
        """استرجاع جميع سندات القبض"""
        return Receipt.query.order_by(Receipt.date.desc()).all()
    
    @staticmethod
    def get_by_client_id(client_id):
        """استرجاع سندات القبض لعميل معين"""
        return Receipt.query.filter_by(client_id=client_id).order_by(Receipt.date.desc()).all()
    
    @staticmethod
    def get_by_contract_id(contract_id):
        """استرجاع سندات القبض لعقد معين"""
        return Receipt.query.filter_by(contract_id=contract_id).order_by(Receipt.date.desc()).all()
    
    @staticmethod
    def get_by_date_range(start_date, end_date):
        """استرجاع سندات القبض ضمن فترة زمنية محددة"""
        return Receipt.query.filter(Receipt.date.between(start_date, end_date)).order_by(Receipt.date).all()
    
    @staticmethod
    def generate_receipt_number():
        """توليد رقم سند قبض فريد"""
        year = datetime.now().year
        month = datetime.now().month
        
        count = Receipt.query.filter(
            Receipt.receipt_number.like(f'REC-{year}{month:02d}-%')
        ).count() + 1
        
        return f'REC-{year}{month:02d}-{count:04d}'
