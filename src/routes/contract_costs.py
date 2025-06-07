"""
مسارات تكاليف العقود لتطبيق الجيل الحديث للأمن والمصاعد
يتيح هذا الملف إدارة مصروفات العقود وربطها بأوامر الشراء
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models.db import db
from src.models.contract import Contract
from src.models.contract_cost import ContractExpense, ContractExpenseType, PurchaseOrderContractLink
from src.models.purchase import PurchaseOrder
from src.routes.auth import admin_required
from datetime import datetime
import json

# إنشاء blueprint لمسارات تكاليف العقود
contract_costs = Blueprint('contract_costs', __name__, url_prefix='/contract-costs')

@contract_costs.route('/expense-types', methods=['GET'])
@login_required
def expense_types():
    """عرض أنواع المصروفات"""
    expense_types = ContractExpenseType.query.all()
    return render_template('contract_costs/expense_types.html', expense_types=expense_types)

@contract_costs.route('/expense-types/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_expense_type():
    """إضافة نوع مصروف جديد"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('يرجى إدخال اسم نوع المصروف', 'danger')
            return redirect(url_for('contract_costs.add_expense_type'))
        
        expense_type = ContractExpenseType(name=name, description=description)
        db.session.add(expense_type)
        
        try:
            db.session.commit()
            flash('تم إضافة نوع المصروف بنجاح', 'success')
            return redirect(url_for('contract_costs.expense_types'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة نوع المصروف: {str(e)}', 'danger')
    
    return render_template('contract_costs/add_expense_type.html')

@contract_costs.route('/contract/<int:contract_id>/expenses', methods=['GET'])
@login_required
def contract_expenses(contract_id):
    """عرض مصروفات العقد"""
    contract = Contract.query.get_or_404(contract_id)
    expenses = ContractExpense.query.filter_by(contract_id=contract_id).all()
    purchase_links = PurchaseOrderContractLink.query.filter_by(contract_id=contract_id).all()
    
    # حساب إجمالي المصروفات
    total_expenses = sum(expense.amount for expense in expenses)
    total_purchases = sum(link.amount_allocated for link in purchase_links)
    total_costs = total_expenses + total_purchases
    
    # حساب الربح
    profit = contract.total_amount - total_costs
    profit_percentage = (profit / contract.total_amount * 100) if contract.total_amount > 0 else 0
    
    return render_template(
        'contract_costs/contract_expenses.html',
        contract=contract,
        expenses=expenses,
        purchase_links=purchase_links,
        total_expenses=total_expenses,
        total_purchases=total_purchases,
        total_costs=total_costs,
        profit=profit,
        profit_percentage=profit_percentage
    )

@contract_costs.route('/contract/<int:contract_id>/add-expense', methods=['GET', 'POST'])
@login_required
def add_contract_expense(contract_id):
    """إضافة مصروف جديد للعقد"""
    contract = Contract.query.get_or_404(contract_id)
    expense_types = ContractExpenseType.query.all()
    
    if request.method == 'POST':
        expense_type_id = request.form.get('expense_type_id')
        amount = request.form.get('amount')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        if not expense_type_id or not amount:
            flash('يرجى إدخال جميع البيانات المطلوبة', 'danger')
            return redirect(url_for('contract_costs.add_contract_expense', contract_id=contract_id))
        
        try:
            amount = float(amount)
            date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
            
            expense = ContractExpense(
                contract_id=contract_id,
                expense_type_id=expense_type_id,
                amount=amount,
                description=description,
                date=date
            )
            db.session.add(expense)
            db.session.commit()
            
            flash('تم إضافة المصروف بنجاح', 'success')
            return redirect(url_for('contract_costs.contract_expenses', contract_id=contract_id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة المصروف: {str(e)}', 'danger')
    
    return render_template(
        'contract_costs/add_contract_expense.html',
        contract=contract,
        expense_types=expense_types
    )

@contract_costs.route('/contract/<int:contract_id>/link-purchase', methods=['GET', 'POST'])
@login_required
def link_purchase_order(contract_id):
    """ربط أمر شراء بالعقد"""
    contract = Contract.query.get_or_404(contract_id)
    
    # الحصول على أوامر الشراء غير المرتبطة بالعقد الحالي
    existing_links = PurchaseOrderContractLink.query.filter_by(contract_id=contract_id).all()
    existing_po_ids = [link.purchase_order_id for link in existing_links]
    
    purchase_orders = PurchaseOrder.query.filter(~PurchaseOrder.id.in_(existing_po_ids)).all() if existing_po_ids else PurchaseOrder.query.all()
    
    if request.method == 'POST':
        purchase_order_id = request.form.get('purchase_order_id')
        amount_allocated = request.form.get('amount_allocated')
        description = request.form.get('description')
        
        if not purchase_order_id or not amount_allocated:
            flash('يرجى إدخال جميع البيانات المطلوبة', 'danger')
            return redirect(url_for('contract_costs.link_purchase_order', contract_id=contract_id))
        
        try:
            amount_allocated = float(amount_allocated)
            
            # التحقق من أن المبلغ المخصص لا يتجاوز قيمة أمر الشراء
            purchase_order = PurchaseOrder.query.get(purchase_order_id)
            if amount_allocated > purchase_order.total_amount:
                flash('المبلغ المخصص يتجاوز قيمة أمر الشراء', 'danger')
                return redirect(url_for('contract_costs.link_purchase_order', contract_id=contract_id))
            
            link = PurchaseOrderContractLink(
                contract_id=contract_id,
                purchase_order_id=purchase_order_id,
                amount_allocated=amount_allocated,
                description=description
            )
            db.session.add(link)
            db.session.commit()
            
            flash('تم ربط أمر الشراء بالعقد بنجاح', 'success')
            return redirect(url_for('contract_costs.contract_expenses', contract_id=contract_id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء ربط أمر الشراء: {str(e)}', 'danger')
    
    return render_template(
        'contract_costs/link_purchase_order.html',
        contract=contract,
        purchase_orders=purchase_orders
    )

@contract_costs.route('/contract/<int:contract_id>/expense/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(contract_id, expense_id):
    """حذف مصروف من العقد"""
    expense = ContractExpense.query.get_or_404(expense_id)
    
    # التحقق من أن المصروف ينتمي للعقد المحدد
    if expense.contract_id != contract_id:
        flash('غير مسموح بحذف هذا المصروف', 'danger')
        return redirect(url_for('contract_costs.contract_expenses', contract_id=contract_id))
    
    try:
        db.session.delete(expense)
        db.session.commit()
        flash('تم حذف المصروف بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المصروف: {str(e)}', 'danger')
    
    return redirect(url_for('contract_costs.contract_expenses', contract_id=contract_id))

@contract_costs.route('/contract/<int:contract_id>/purchase-link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_purchase_link(contract_id, link_id):
    """حذف ربط أمر شراء من العقد"""
    link = PurchaseOrderContractLink.query.get_or_404(link_id)
    
    # التحقق من أن الربط ينتمي للعقد المحدد
    if link.contract_id != contract_id:
        flash('غير مسموح بحذف هذا الربط', 'danger')
        return redirect(url_for('contract_costs.contract_expenses', contract_id=contract_id))
    
    try:
        db.session.delete(link)
        db.session.commit()
        flash('تم حذف ربط أمر الشراء بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف ربط أمر الشراء: {str(e)}', 'danger')
    
    return redirect(url_for('contract_costs.contract_expenses', contract_id=contract_id))

@contract_costs.route('/contract/<int:contract_id>/cost-report', methods=['GET'])
@login_required
def contract_cost_report(contract_id):
    """عرض تقرير تكاليف العقد"""
    contract = Contract.query.get_or_404(contract_id)
    expenses = ContractExpense.query.filter_by(contract_id=contract_id).all()
    purchase_links = PurchaseOrderContractLink.query.filter_by(contract_id=contract_id).all()
    
    # تجميع المصروفات حسب النوع
    expense_by_type = {}
    for expense in expenses:
        type_name = expense.expense_type.name
        if type_name not in expense_by_type:
            expense_by_type[type_name] = 0
        expense_by_type[type_name] += expense.amount
    
    # حساب إجمالي المصروفات
    total_expenses = sum(expense.amount for expense in expenses)
    total_purchases = sum(link.amount_allocated for link in purchase_links)
    total_costs = total_expenses + total_purchases
    
    # حساب الربح
    profit = contract.total_amount - total_costs
    profit_percentage = (profit / contract.total_amount * 100) if contract.total_amount > 0 else 0
    
    # إعداد بيانات الرسم البياني
    chart_data = {
        'expense_types': list(expense_by_type.keys()),
        'expense_amounts': list(expense_by_type.values()),
        'summary': [
            {'name': 'إجمالي قيمة العقد', 'value': contract.total_amount},
            {'name': 'إجمالي المصروفات', 'value': total_expenses},
            {'name': 'إجمالي المشتريات', 'value': total_purchases},
            {'name': 'إجمالي التكاليف', 'value': total_costs},
            {'name': 'صافي الربح', 'value': profit}
        ]
    }
    
    return render_template(
        'contract_costs/cost_report.html',
        contract=contract,
        expenses=expenses,
        purchase_links=purchase_links,
        expense_by_type=expense_by_type,
        total_expenses=total_expenses,
        total_purchases=total_purchases,
        total_costs=total_costs,
        profit=profit,
        profit_percentage=profit_percentage,
        chart_data=json.dumps(chart_data)
    )

@contract_costs.route('/contract/<int:contract_id>/print-cost-report', methods=['GET'])
@login_required
def print_cost_report(contract_id):
    """طباعة تقرير تكاليف العقد"""
    contract = Contract.query.get_or_404(contract_id)
    expenses = ContractExpense.query.filter_by(contract_id=contract_id).all()
    purchase_links = PurchaseOrderContractLink.query.filter_by(contract_id=contract_id).all()
    
    # تجميع المصروفات حسب النوع
    expense_by_type = {}
    for expense in expenses:
        type_name = expense.expense_type.name
        if type_name not in expense_by_type:
            expense_by_type[type_name] = 0
        expense_by_type[type_name] += expense.amount
    
    # حساب إجمالي المصروفات
    total_expenses = sum(expense.amount for expense in expenses)
    total_purchases = sum(link.amount_allocated for link in purchase_links)
    total_costs = total_expenses + total_purchases
    
    # حساب الربح
    profit = contract.total_amount - total_costs
    profit_percentage = (profit / contract.total_amount * 100) if contract.total_amount > 0 else 0
    
    return render_template(
        'contract_costs/print_cost_report.html',
        contract=contract,
        expenses=expenses,
        purchase_links=purchase_links,
        expense_by_type=expense_by_type,
        total_expenses=total_expenses,
        total_purchases=total_purchases,
        total_costs=total_costs,
        profit=profit,
        profit_percentage=profit_percentage
    )
