"""
نموذج تكاليف العقود لتطبيق الجيل الحديث للأمن والمصاعد
يتيح هذا النموذج تتبع جميع المصروفات والمشتريات المرتبطة بكل عقد
"""

from datetime import datetime
from src.models.db import db
from src.models.contract import Contract

class ContractExpenseType(db.Model):
    """نموذج أنواع المصروفات للعقود"""
    __tablename__ = 'contract_expense_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # العلاقات
    expenses = db.relationship('ContractExpense', backref='expense_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<نوع المصروف: {self.name}>'

class ContractExpense(db.Model):
    """نموذج مصروفات العقود"""
    __tablename__ = 'contract_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('contract_expense_types.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<مصروف عقد: {self.amount} - {self.description}>'

class PurchaseOrderContractLink(db.Model):
    """نموذج ربط أوامر الشراء بالعقود"""
    __tablename__ = 'purchase_order_contract_links'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    amount_allocated = db.Column(db.Float, nullable=False)  # المبلغ المخصص من أمر الشراء لهذا العقد
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    contract = db.relationship('Contract', backref=db.backref('purchase_order_links', lazy='dynamic'))
    purchase_order = db.relationship('PurchaseOrder', backref=db.backref('contract_links', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ربط أمر شراء بعقد: {self.purchase_order_id} - {self.contract_id}>'

# تحديث نموذج العقد لإضافة العلاقات الجديدة
def update_contract_model():
    """تحديث نموذج العقد لإضافة العلاقات الجديدة"""
    # إضافة العلاقات للمصروفات وأوامر الشراء
    if not hasattr(Contract, 'expenses'):
        Contract.expenses = db.relationship('ContractExpense', backref='contract', lazy='dynamic')
