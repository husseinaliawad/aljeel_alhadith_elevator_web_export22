"""
تكامل نظام إدارة المستندات مع نظام العقود
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models.db import db
from src.models.document import Document, DocumentEntityLink
from src.models.contract import Contract

# إنشاء blueprint للتكامل بين المستندات والعقود
document_contract_integration = Blueprint('document_contract_integration', __name__)

@document_contract_integration.route('/contracts/<int:contract_id>/documents', methods=['GET'])
@login_required
def contract_documents(contract_id):
    """عرض المستندات المرتبطة بعقد محدد"""
    contract = Contract.query.get_or_404(contract_id)
    
    # الحصول على المستندات المرتبطة بالعقد
    document_links = DocumentEntityLink.query.filter_by(
        entity_type='contract',
        entity_id=contract_id
    ).all()
    
    document_ids = [link.document_id for link in document_links]
    documents = Document.query.filter(Document.id.in_(document_ids)).all()
    
    # الحصول على جميع المستندات المتاحة للربط
    available_documents = Document.query.filter(~Document.id.in_(document_ids)).all()
    
    return render_template(
        'documents/contract_documents.html',
        contract=contract,
        documents=documents,
        available_documents=available_documents
    )

@document_contract_integration.route('/contracts/<int:contract_id>/documents/link', methods=['POST'])
@login_required
def link_document_to_contract(contract_id):
    """ربط مستند بعقد محدد"""
    contract = Contract.query.get_or_404(contract_id)
    document_id = request.form.get('document_id', type=int)
    
    if not document_id:
        flash('يرجى اختيار مستند للربط', 'danger')
        return redirect(url_for('document_contract_integration.contract_documents', contract_id=contract_id))
    
    # التحقق من وجود المستند
    document = Document.query.get_or_404(document_id)
    
    # التحقق من وجود الربط مسبقاً
    existing_link = DocumentEntityLink.query.filter_by(
        document_id=document_id,
        entity_type='contract',
        entity_id=contract_id
    ).first()
    
    if existing_link:
        flash('المستند مرتبط بالفعل بهذا العقد', 'warning')
        return redirect(url_for('document_contract_integration.contract_documents', contract_id=contract_id))
    
    try:
        # إنشاء الربط
        link = DocumentEntityLink(
            document_id=document_id,
            entity_type='contract',
            entity_id=contract_id
        )
        
        db.session.add(link)
        db.session.commit()
        
        flash(f'تم ربط المستند "{document.title}" بالعقد بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء ربط المستند: {str(e)}', 'danger')
    
    return redirect(url_for('document_contract_integration.contract_documents', contract_id=contract_id))

@document_contract_integration.route('/contracts/<int:contract_id>/documents/<int:document_id>/unlink', methods=['POST'])
@login_required
def unlink_document_from_contract(contract_id, document_id):
    """إلغاء ربط مستند من عقد محدد"""
    # التحقق من وجود العقد والمستند
    contract = Contract.query.get_or_404(contract_id)
    document = Document.query.get_or_404(document_id)
    
    # البحث عن الربط
    link = DocumentEntityLink.query.filter_by(
        document_id=document_id,
        entity_type='contract',
        entity_id=contract_id
    ).first_or_404()
    
    try:
        # حذف الربط
        db.session.delete(link)
        db.session.commit()
        
        flash(f'تم إلغاء ربط المستند "{document.title}" من العقد بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إلغاء ربط المستند: {str(e)}', 'danger')
    
    return redirect(url_for('document_contract_integration.contract_documents', contract_id=contract_id))

@document_contract_integration.route('/contracts/<int:contract_id>/documents/upload', methods=['GET', 'POST'])
@login_required
def upload_contract_document(contract_id):
    """رفع مستند جديد وربطه بعقد محدد"""
    contract = Contract.query.get_or_404(contract_id)
    
    if request.method == 'POST':
        # استخدام وظيفة إضافة المستند الموجودة مع إضافة الربط بالعقد
        # هذا الكود يفترض أن هناك وظيفة add_document موجودة بالفعل
        # يمكن تعديله حسب الحاجة
        
        # بعد إضافة المستند، يتم إنشاء الربط
        # document_id = result_of_add_document()
        # 
        # link = DocumentEntityLink(
        #     document_id=document_id,
        #     entity_type='contract',
        #     entity_id=contract_id
        # )
        # 
        # db.session.add(link)
        # db.session.commit()
        
        # لأغراض هذا المثال، سنعيد توجيه المستخدم إلى صفحة إضافة مستند
        # مع تمرير معلومات العقد كمعلمات استعلام
        return redirect(url_for('documents.add_document', contract_id=contract_id, entity_type='contract'))
    
    return render_template(
        'documents/upload_contract_document.html',
        contract=contract
    )

# تعديل مسار عرض العقد لإضافة علامة تبويب للمستندات
def modify_contract_view():
    """
    هذه الوظيفة ليست مساراً فعلياً، بل هي توضيح لكيفية تعديل
    مسار عرض العقد لإضافة علامة تبويب للمستندات
    
    يجب تعديل مسار contracts.view_contract لإضافة:
    
    # الحصول على المستندات المرتبطة بالعقد
    document_links = DocumentEntityLink.query.filter_by(
        entity_type='contract',
        entity_id=contract_id
    ).all()
    
    document_ids = [link.document_id for link in document_links]
    documents = Document.query.filter(Document.id.in_(document_ids)).all()
    
    # إضافة المستندات إلى قالب العرض
    return render_template(
        'contracts/view_contract.html',
        contract=contract,
        ...,
        documents=documents
    )
    """
    pass
