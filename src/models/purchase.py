"""
نموذج المشتريات لتطبيق الجيل الحديث للأمن والمصاعد
"""
from datetime import datetime
from src.models.db import db
from src.models.user import User

class Supplier(db.Model):
    """نموذج الموردين"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    tax_number = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'tax_number': self.tax_number,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class PurchaseOrder(db.Model):
    """نموذج أوامر الشراء"""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), nullable=False, unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    expected_delivery_date = db.Column(db.Date, nullable=True)
    delivery_address = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, approved, sent, received, cancelled
    total_amount = db.Column(db.Float, nullable=False, default=0)
    tax_amount = db.Column(db.Float, nullable=False, default=0)
    discount_amount = db.Column(db.Float, nullable=False, default=0)
    final_amount = db.Column(db.Float, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='purchase_orders', lazy=True)
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PurchaseOrder {self.order_number}>'
    
    def calculate_totals(self):
        """حساب المجاميع"""
        self.total_amount = sum(item.total_price for item in self.items)
        self.final_amount = self.total_amount + self.tax_amount - self.discount_amount
        return self.final_amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'order_date': self.order_date.strftime('%Y-%m-%d') if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.strftime('%Y-%m-%d') if self.expected_delivery_date else None,
            'delivery_address': self.delivery_address,
            'status': self.status,
            'total_amount': self.total_amount,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'final_amount': self.final_amount,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class PurchaseOrderItem(db.Model):
    """نموذج عناصر أمر الشراء"""
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=True)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    # العلاقات
    part = db.relationship('Part', backref='purchase_order_items', lazy=True)
    
    def __repr__(self):
        return f'<PurchaseOrderItem {self.description}>'
    
    def calculate_total(self):
        """حساب المجموع"""
        self.total_price = self.quantity * self.unit_price
        return self.total_price
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'part_id': self.part_id,
            'part_name': self.part.name if self.part else None,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'notes': self.notes
        }


class PurchaseReceive(db.Model):
    """نموذج استلام المشتريات"""
    __tablename__ = 'purchase_receives'
    
    id = db.Column(db.Integer, primary_key=True)
    receive_number = db.Column(db.String(50), nullable=False, unique=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receive_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), nullable=False, default='received')  # received, partial, rejected
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    purchase_order = db.relationship('PurchaseOrder', backref='receives', lazy=True)
    user = db.relationship('User', backref='purchase_receives', lazy=True)
    items = db.relationship('PurchaseReceiveItem', backref='purchase_receive', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PurchaseReceive {self.receive_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'receive_number': self.receive_number,
            'purchase_order_id': self.purchase_order_id,
            'purchase_order_number': self.purchase_order.order_number if self.purchase_order else None,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'receive_date': self.receive_date.strftime('%Y-%m-%d') if self.receive_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class PurchaseReceiveItem(db.Model):
    """نموذج عناصر استلام المشتريات"""
    __tablename__ = 'purchase_receive_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_receive_id = db.Column(db.Integer, db.ForeignKey('purchase_receives.id'), nullable=False)
    purchase_order_item_id = db.Column(db.Integer, db.ForeignKey('purchase_order_items.id'), nullable=False)
    quantity_received = db.Column(db.Float, nullable=False)
    quality_status = db.Column(db.String(20), nullable=False, default='accepted')  # accepted, rejected, damaged
    notes = db.Column(db.Text, nullable=True)
    
    # العلاقات
    purchase_order_item = db.relationship('PurchaseOrderItem', backref='receive_items', lazy=True)
    
    def __repr__(self):
        return f'<PurchaseReceiveItem {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchase_receive_id': self.purchase_receive_id,
            'purchase_order_item_id': self.purchase_order_item_id,
            'description': self.purchase_order_item.description if self.purchase_order_item else None,
            'quantity_ordered': self.purchase_order_item.quantity if self.purchase_order_item else None,
            'quantity_received': self.quantity_received,
            'quality_status': self.quality_status,
            'notes': self.notes
        }
