"""
نموذج العقود لتطبيق aljeel alhadith elevator
"""
from datetime import datetime
from src.models.db import db
import json

class Contract(db.Model):
    """نموذج العقود"""
    
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_number = db.Column(db.String(50), nullable=False, unique=True)
    client_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    contract_type = db.Column(db.String(50), nullable=False)
    contract_value = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.Text, nullable=True)
    elevator_ids = db.Column(db.Text, nullable=True)  # سيتم تخزينها كسلسلة JSON
    status = db.Column(db.String(20), default="ساري")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, contract_number=None, client_name=None, start_date=None, 
                 end_date=None, contract_type=None, contract_value=0.0, payment_terms=None, 
                 elevator_ids=None, status="ساري", notes=None):
        """
        تهيئة كائن العقد
        
        المعلمات:
            contract_number (str): رقم العقد
            client_name (str): اسم العميل
            start_date (str): تاريخ بداية العقد
            end_date (str): تاريخ نهاية العقد
            contract_type (str): نوع العقد (مثل: صيانة دورية، صيانة شاملة، تركيب)
            contract_value (float): قيمة العقد
            payment_terms (str): شروط الدفع
            elevator_ids (list): قائمة معرفات المصاعد المشمولة في العقد
            status (str): حالة العقد (مثل: ساري، منتهي، ملغي)
            notes (str): ملاحظات إضافية (اختياري)
        """
        self.contract_number = contract_number
        self.client_name = client_name
        self.start_date = start_date
        self.end_date = end_date
        self.contract_type = contract_type
        self.contract_value = contract_value
        self.payment_terms = payment_terms
        self.elevator_ids = json.dumps(elevator_ids) if elevator_ids else json.dumps([])
        self.status = status
        self.notes = notes
    
    def get_elevator_ids(self):
        """
        الحصول على قائمة معرفات المصاعد
        
        العائد:
            list: قائمة معرفات المصاعد
        """
        return json.loads(self.elevator_ids) if self.elevator_ids else []
    
    def set_elevator_ids(self, elevator_ids):
        """
        تعيين قائمة معرفات المصاعد
        
        المعلمات:
            elevator_ids (list): قائمة معرفات المصاعد
        """
        self.elevator_ids = json.dumps(elevator_ids)
        
    def is_active(self):
        """
        التحقق مما إذا كان العقد ساري المفعول
        
        العائد:
            bool: True إذا كان العقد ساري المفعول، False خلاف ذلك
        """
        if self.status != "ساري":
            return False
            
        today = datetime.now().strftime("%Y-%m-%d")
        return self.start_date <= today <= self.end_date
        
    def days_until_expiry(self):
        """
        حساب عدد الأيام المتبقية حتى انتهاء العقد
        
        العائد:
            int: عدد الأيام المتبقية، أو -1 إذا كان العقد منتهي
        """
        if not self.is_active():
            return -1
            
        today = datetime.now()
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        delta = end_date - today
        return delta.days
        
    def to_dict(self):
        """
        تحويل الكائن إلى قاموس
        
        العائد:
            dict: قاموس يمثل العقد
        """
        return {
            'id': self.id,
            'contract_number': self.contract_number,
            'client_name': self.client_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'contract_type': self.contract_type,
            'contract_value': self.contract_value,
            'payment_terms': self.payment_terms,
            'elevator_ids': self.get_elevator_ids(),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
