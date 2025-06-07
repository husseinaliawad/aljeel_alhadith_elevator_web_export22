"""
مسارات المشتريات لتطبيق الجيل الحديث للأمن والمصاعد
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from src.models.purchase import Supplier, PurchaseOrder, PurchaseOrderItem, PurchaseReceive, PurchaseReceiveItem
from src.models.part import Part
from src.models.db import db
from src.routes.auth import login_required, admin_required
from datetime import datetime
import uuid

# إنشاء blueprint للمشتريات
purchases = Blueprint('purchases', __name__)

# صفحة الموردين
@purchases.route('/suppliers')
@login_required
def suppliers():
    suppliers_list = Supplier.query.all()
    return render_template('purchases/suppliers.html', suppliers=suppliers_list)

# إضافة مورد جديد
@purchases.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        tax_number = request.form.get('tax_number')
        notes = request.form.get('notes')
        
        new_supplier = Supplier(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            tax_number=tax_number,
            notes=notes
        )
        
        db.session.add(new_supplier)
        db.session.commit()
        
        flash('تم إضافة المورد بنجاح', 'success')
        return redirect(url_for('purchases.suppliers'))
    
    return render_template('purchases/add_supplier.html')

# تعديل مورد
@purchases.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.contact_person = request.form.get('contact_person')
        supplier.email = request.form.get('email')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')
        supplier.tax_number = request.form.get('tax_number')
        supplier.notes = request.form.get('notes')
        supplier.is_active = 'is_active' in request.form
        
        db.session.commit()
        
        flash('تم تحديث بيانات المورد بنجاح', 'success')
        return redirect(url_for('purchases.suppliers'))
    
    return render_template('purchases/edit_supplier.html', supplier=supplier)

# حذف مورد
@purchases.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # التحقق من عدم وجود أوامر شراء مرتبطة بالمورد
    if supplier.purchase_orders:
        flash('لا يمكن حذف المورد لوجود أوامر شراء مرتبطة به', 'danger')
        return redirect(url_for('purchases.suppliers'))
    
    db.session.delete(supplier)
    db.session.commit()
    
    flash('تم حذف المورد بنجاح', 'success')
    return redirect(url_for('purchases.suppliers'))

# صفحة أوامر الشراء
@purchases.route('/purchase-orders')
@login_required
def purchase_orders():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('purchases/purchase_orders.html', orders=orders)

# إضافة أمر شراء جديد
@purchases.route('/purchase-orders/add', methods=['GET', 'POST'])
@login_required
def add_purchase_order():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        order_date = datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date()
        expected_delivery_date = datetime.strptime(request.form.get('expected_delivery_date'), '%Y-%m-%d').date() if request.form.get('expected_delivery_date') else None
        delivery_address = request.form.get('delivery_address')
        notes = request.form.get('notes')
        
        # إنشاء رقم أمر شراء فريد
        order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
        
        new_order = PurchaseOrder(
            order_number=order_number,
            supplier_id=supplier_id,
            user_id=session['user_id'],
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            delivery_address=delivery_address,
            notes=notes,
            status='draft'
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        flash('تم إنشاء أمر الشراء بنجاح', 'success')
        return redirect(url_for('purchases.edit_purchase_order', order_id=new_order.id))
    
    suppliers = Supplier.query.filter_by(is_active=True).all()
    return render_template('purchases/add_purchase_order.html', suppliers=suppliers)

# عرض أمر شراء
@purchases.route('/purchase-orders/<int:order_id>')
@login_required
def view_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    return render_template('purchases/view_purchase_order.html', order=order)

# تعديل أمر شراء
@purchases.route('/purchase-orders/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # التحقق من أن أمر الشراء في حالة مسودة
    if order.status != 'draft':
        flash('لا يمكن تعديل أمر الشراء بعد اعتماده', 'danger')
        return redirect(url_for('purchases.view_purchase_order', order_id=order_id))
    
    if request.method == 'POST':
        order.supplier_id = request.form.get('supplier_id')
        order.order_date = datetime.strptime(request.form.get('order_date'), '%Y-%m-%d').date()
        order.expected_delivery_date = datetime.strptime(request.form.get('expected_delivery_date'), '%Y-%m-%d').date() if request.form.get('expected_delivery_date') else None
        order.delivery_address = request.form.get('delivery_address')
        order.notes = request.form.get('notes')
        
        db.session.commit()
        
        flash('تم تحديث أمر الشراء بنجاح', 'success')
        return redirect(url_for('purchases.view_purchase_order', order_id=order_id))
    
    suppliers = Supplier.query.filter_by(is_active=True).all()
    parts = Part.query.all()
    return render_template('purchases/edit_purchase_order.html', order=order, suppliers=suppliers, parts=parts)

# إضافة عنصر إلى أمر الشراء
@purchases.route('/purchase-orders/<int:order_id>/add-item', methods=['POST'])
@login_required
def add_purchase_order_item(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # التحقق من أن أمر الشراء في حالة مسودة
    if order.status != 'draft':
        flash('لا يمكن تعديل أمر الشراء بعد اعتماده', 'danger')
        return redirect(url_for('purchases.view_purchase_order', order_id=order_id))
    
    part_id = request.form.get('part_id')
    description = request.form.get('description')
    quantity = float(request.form.get('quantity'))
    unit = request.form.get('unit')
    unit_price = float(request.form.get('unit_price'))
    notes = request.form.get('notes')
    
    # حساب السعر الإجمالي
    total_price = quantity * unit_price
    
    new_item = PurchaseOrderItem(
        purchase_order_id=order_id,
        part_id=part_id if part_id else None,
        description=description,
        quantity=quantity,
        unit=unit,
        unit_price=unit_price,
        total_price=total_price,
        notes=notes
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    # إعادة حساب المجاميع
    order.calculate_totals()
    db.session.commit()
    
    flash('تم إضافة العنصر بنجاح', 'success')
    return redirect(url_for('purchases.edit_purchase_order', order_id=order_id))

# حذف عنصر من أمر الشراء
@purchases.route('/purchase-orders/items/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_purchase_order_item(item_id):
    item = PurchaseOrderItem.query.get_or_404(item_id)
    order_id = item.purchase_order_id
    order = PurchaseOrder.query.get(order_id)
    
    # التحقق من أن أمر الشراء في حالة مسودة
    if order.status != 'draft':
        flash('لا يمكن تعديل أمر الشراء بعد اعتماده', 'danger')
        return redirect(url_for('purchases.view_purchase_order', order_id=order_id))
    
    db.session.delete(item)
    db.session.commit()
    
    # إعادة حساب المجاميع
    order.calculate_totals()
    db.session.commit()
    
    flash('تم حذف العنصر بنجاح', 'success')
    return redirect(url_for('purchases.edit_purchase_order', order_id=order_id))

# تحديث حالة أمر الشراء
@purchases.route('/purchase-orders/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_purchase_order_status(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    # التحقق من صحة الحالة الجديدة
    valid_statuses = ['draft', 'approved', 'sent', 'received', 'cancelled']
    if new_status not in valid_statuses:
        flash('حالة غير صالحة', 'danger')
        return redirect(url_for('purchases.view_purchase_order', order_id=order_id))
    
    order.status = new_status
    db.session.commit()
    
    flash('تم تحديث حالة أمر الشراء بنجاح', 'success')
    return redirect(url_for('purchases.view_purchase_order', order_id=order_id))

# طباعة أمر الشراء
@purchases.route('/purchase-orders/<int:order_id>/print')
@login_required
def print_purchase_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    return render_template('purchases/print_purchase_order.html', order=order)

# صفحة استلام المشتريات
@purchases.route('/purchase-receives')
@login_required
def purchase_receives():
    receives = PurchaseReceive.query.order_by(PurchaseReceive.created_at.desc()).all()
    return render_template('purchases/purchase_receives.html', receives=receives)

# إضافة استلام جديد
@purchases.route('/purchase-receives/add', methods=['GET', 'POST'])
@login_required
def add_purchase_receive():
    if request.method == 'POST':
        purchase_order_id = request.form.get('purchase_order_id')
        receive_date = datetime.strptime(request.form.get('receive_date'), '%Y-%m-%d').date()
        notes = request.form.get('notes')
        
        # التحقق من وجود أمر الشراء
        order = PurchaseOrder.query.get(purchase_order_id)
        if not order:
            flash('أمر الشراء غير موجود', 'danger')
            return redirect(url_for('purchases.purchase_receives'))
        
        # إنشاء رقم استلام فريد
        receive_number = f"RCV-{uuid.uuid4().hex[:8].upper()}"
        
        new_receive = PurchaseReceive(
            receive_number=receive_number,
            purchase_order_id=purchase_order_id,
            user_id=session['user_id'],
            receive_date=receive_date,
            notes=notes,
            status='received'
        )
        
        db.session.add(new_receive)
        db.session.commit()
        
        flash('تم إنشاء استلام المشتريات بنجاح', 'success')
        return redirect(url_for('purchases.edit_purchase_receive', receive_id=new_receive.id))
    
    # الحصول على أوامر الشراء المرسلة
    orders = PurchaseOrder.query.filter_by(status='sent').all()
    return render_template('purchases/add_purchase_receive.html', orders=orders)

# عرض استلام المشتريات
@purchases.route('/purchase-receives/<int:receive_id>')
@login_required
def view_purchase_receive(receive_id):
    receive = PurchaseReceive.query.get_or_404(receive_id)
    return render_template('purchases/view_purchase_receive.html', receive=receive)

# تعديل استلام المشتريات
@purchases.route('/purchase-receives/edit/<int:receive_id>', methods=['GET', 'POST'])
@login_required
def edit_purchase_receive(receive_id):
    receive = PurchaseReceive.query.get_or_404(receive_id)
    
    if request.method == 'POST':
        receive.receive_date = datetime.strptime(request.form.get('receive_date'), '%Y-%m-%d').date()
        receive.notes = request.form.get('notes')
        
        db.session.commit()
        
        flash('تم تحديث استلام المشتريات بنجاح', 'success')
        return redirect(url_for('purchases.view_purchase_receive', receive_id=receive_id))
    
    # الحصول على عناصر أمر الشراء
    order_items = PurchaseOrderItem.query.filter_by(purchase_order_id=receive.purchase_order_id).all()
    return render_template('purchases/edit_purchase_receive.html', receive=receive, order_items=order_items)

# إضافة عنصر إلى استلام المشتريات
@purchases.route('/purchase-receives/<int:receive_id>/add-item', methods=['POST'])
@login_required
def add_purchase_receive_item(receive_id):
    receive = PurchaseReceive.query.get_or_404(receive_id)
    
    purchase_order_item_id = request.form.get('purchase_order_item_id')
    quantity_received = float(request.form.get('quantity_received'))
    quality_status = request.form.get('quality_status')
    notes = request.form.get('notes')
    
    # التحقق من وجود عنصر أمر الشراء
    order_item = PurchaseOrderItem.query.get(purchase_order_item_id)
    if not order_item:
        flash('عنصر أمر الشراء غير موجود', 'danger')
        return redirect(url_for('purchases.edit_purchase_receive', receive_id=receive_id))
    
    # التحقق من عدم وجود عنصر استلام لنفس عنصر أمر الشراء
    existing_item = PurchaseReceiveItem.query.filter_by(
        purchase_receive_id=receive_id,
        purchase_order_item_id=purchase_order_item_id
    ).first()
    
    if existing_item:
        flash('تم استلام هذا العنصر بالفعل', 'danger')
        return redirect(url_for('purchases.edit_purchase_receive', receive_id=receive_id))
    
    new_item = PurchaseReceiveItem(
        purchase_receive_id=receive_id,
        purchase_order_item_id=purchase_order_item_id,
        quantity_received=quantity_received,
        quality_status=quality_status,
        notes=notes
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    # تحديث المخزون إذا كان العنصر مقبولاً
    if quality_status == 'accepted' and order_item.part_id:
        part = Part.query.get(order_item.part_id)
        if part:
            part.stock_quantity += quantity_received
            db.session.commit()
    
    flash('تم إضافة عنصر الاستلام بنجاح', 'success')
    return redirect(url_for('purchases.edit_purchase_receive', receive_id=receive_id))

# حذف عنصر من استلام المشتريات
@purchases.route('/purchase-receives/items/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_purchase_receive_item(item_id):
    item = PurchaseReceiveItem.query.get_or_404(item_id)
    receive_id = item.purchase_receive_id
    
    # إعادة الكمية إلى المخزون إذا كان العنصر مقبولاً
    if item.quality_status == 'accepted' and item.purchase_order_item.part_id:
        part = Part.query.get(item.purchase_order_item.part_id)
        if part:
            part.stock_quantity -= item.quantity_received
            db.session.commit()
    
    db.session.delete(item)
    db.session.commit()
    
    flash('تم حذف عنصر الاستلام بنجاح', 'success')
    return redirect(url_for('purchases.edit_purchase_receive', receive_id=receive_id))

# طباعة استلام المشتريات
@purchases.route('/purchase-receives/<int:receive_id>/print')
@login_required
def print_purchase_receive(receive_id):
    receive = PurchaseReceive.query.get_or_404(receive_id)
    return render_template('purchases/print_purchase_receive.html', receive=receive)

# واجهة برمجة التطبيقات للموردين
@purchases.route('/api/suppliers', methods=['GET'])
@login_required
def api_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([supplier.to_dict() for supplier in suppliers])

# واجهة برمجة التطبيقات لأوامر الشراء
@purchases.route('/api/purchase-orders', methods=['GET'])
@login_required
def api_purchase_orders():
    orders = PurchaseOrder.query.all()
    return jsonify([order.to_dict() for order in orders])

# واجهة برمجة التطبيقات لاستلام المشتريات
@purchases.route('/api/purchase-receives', methods=['GET'])
@login_required
def api_purchase_receives():
    receives = PurchaseReceive.query.all()
    return jsonify([receive.to_dict() for receive in receives])
