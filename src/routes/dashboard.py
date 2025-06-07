"""
مسارات لوحة المعلومات الرئيسية لتطبيق aljeel alhadith elevator
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app as app
from src.models.elevator import Elevator
from src.models.maintenance_request import MaintenanceRequest
from src.models.part import Part
from src.models.contract import Contract
from src.models.scheduled_maintenance import ScheduledMaintenance
from src.routes.auth import login_required
from src.models.db import db
from datetime import datetime, timedelta
import json

# إنشاء blueprint للوحة المعلومات
dashboard = Blueprint('dashboard', __name__)

# الصفحة الرئيسية
@dashboard.route('/')
def index():
    return redirect(url_for('dashboard.dashboard_view'))

# لوحة المعلومات
@dashboard.route('/dashboard')
# @login_required - تم إزالة متطلب تسجيل الدخول مؤقتاً
def dashboard_view():
    # إحصائيات المصاعد
    total_elevators = Elevator.query.count()
    working_elevators = Elevator.query.filter_by(status="يعمل").count()
    maintenance_elevators = Elevator.query.filter_by(status="قيد الصيانة").count()
    stopped_elevators = Elevator.query.filter_by(status="متوقف").count()
    
    # إحصائيات طلبات الصيانة
    total_requests = MaintenanceRequest.query.count()
    new_requests = MaintenanceRequest.query.filter_by(status="جديد").count()
    in_progress_requests = MaintenanceRequest.query.filter_by(status="قيد المعالجة").count()
    completed_requests = MaintenanceRequest.query.filter_by(status="مكتمل").count()
    
    # قطع الغيار منخفضة المخزون
    low_stock_parts = Part.query.filter(Part.quantity < Part.min_quantity).all()
    
    # العقود القريبة من الانتهاء (خلال 30 يوم)
    today = datetime.now().strftime("%Y-%m-%d")
    thirty_days_later = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    expiring_contracts = Contract.query.filter(
        Contract.status == "ساري",
        Contract.end_date >= today,
        Contract.end_date <= thirty_days_later
    ).all()
    
    # الصيانة المجدولة القادمة (خلال 7 أيام)
    seven_days_later = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    upcoming_maintenance = ScheduledMaintenance.query.filter(
        ScheduledMaintenance.status == "مجدولة",
        ScheduledMaintenance.scheduled_date >= today,
        ScheduledMaintenance.scheduled_date <= seven_days_later
    ).all()
    
    # طلبات الصيانة الأخيرة
    recent_requests = MaintenanceRequest.query.order_by(MaintenanceRequest.id.desc()).limit(5).all()
    
    # بيانات الرسوم البيانية
    # 1. توزيع حالات المصاعد
    elevator_status_data = {
        'labels': ['يعمل', 'قيد الصيانة', 'متوقف'],
        'data': [working_elevators, maintenance_elevators, stopped_elevators]
    }
    
    # 2. توزيع حالات طلبات الصيانة
    request_status_data = {
        'labels': ['جديد', 'قيد المعالجة', 'مكتمل'],
        'data': [new_requests, in_progress_requests, completed_requests]
    }
    
    # إضافة متغير chart_data المطلوب في القالب - تم تبسيطه لتجنب مشاكل التحويل إلى JSON
    chart_data = {}
    chart_data['labels'] = ['يعمل', 'قيد الصيانة', 'متوقف', 'جديد', 'قيد المعالجة', 'مكتمل']
    chart_data['values'] = [1, 2, 3, 4, 5, 6]  # قيم ثابتة للتجربة
    
    # إضافة سجل للتشخيص
    app.logger.info('تم تحضير بيانات الرسم البياني: %s', chart_data)
    
    # إضافة متغير stats المطلوب في القالب
    stats = {
        'elevators_count': total_elevators,
        'pending_requests': new_requests + in_progress_requests,
        'active_contracts': Contract.query.filter_by(status="ساري").count(),
        'low_stock_parts': len(low_stock_parts)
    }
    
    # إضافة متغير current_requests المطلوب في القالب
    current_requests = MaintenanceRequest.query.filter(
        MaintenanceRequest.status.in_(["جديد", "قيد المعالجة"])
    ).order_by(MaintenanceRequest.id.desc()).limit(5).all()
    
    return render_template('dashboard/index.html',
                          total_elevators=total_elevators,
                          working_elevators=working_elevators,
                          maintenance_elevators=maintenance_elevators,
                          stopped_elevators=stopped_elevators,
                          total_requests=total_requests,
                          new_requests=new_requests,
                          in_progress_requests=in_progress_requests,
                          completed_requests=completed_requests,
                          low_stock_parts=low_stock_parts,
                          expiring_contracts=expiring_contracts,
                          upcoming_maintenance=upcoming_maintenance,
                          recent_requests=recent_requests,
                          elevator_status_data=json.dumps(elevator_status_data),
                          request_status_data=json.dumps(request_status_data),
                          chart_data=chart_data,
                          stats=stats,
                          current_requests=current_requests)

# واجهة برمجة التطبيقات للإحصائيات
@dashboard.route('/api/stats')
# @login_required - تم إزالة متطلب تسجيل الدخول مؤقتاً
def api_stats():
    # إحصائيات المصاعد
    total_elevators = Elevator.query.count()
    working_elevators = Elevator.query.filter_by(status="يعمل").count()
    maintenance_elevators = Elevator.query.filter_by(status="قيد الصيانة").count()
    stopped_elevators = Elevator.query.filter_by(status="متوقف").count()
    
    # إحصائيات طلبات الصيانة
    total_requests = MaintenanceRequest.query.count()
    new_requests = MaintenanceRequest.query.filter_by(status="جديد").count()
    in_progress_requests = MaintenanceRequest.query.filter_by(status="قيد المعالجة").count()
    completed_requests = MaintenanceRequest.query.filter_by(status="مكتمل").count()
    
    # قطع الغيار منخفضة المخزون
    low_stock_count = Part.query.filter(Part.quantity < Part.min_quantity).count()
    
    # العقود القريبة من الانتهاء (خلال 30 يوم)
    today = datetime.now().strftime("%Y-%m-%d")
    thirty_days_later = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    expiring_contracts_count = Contract.query.filter(
        Contract.status == "ساري",
        Contract.end_date >= today,
        Contract.end_date <= thirty_days_later
    ).count()
    
    return jsonify({
        'elevators': {
            'total': total_elevators,
            'working': working_elevators,
            'maintenance': maintenance_elevators,
            'stopped': stopped_elevators
        },
        'requests': {
            'total': total_requests,
            'new': new_requests,
            'in_progress': in_progress_requests,
            'completed': completed_requests
        },
        'low_stock_parts': low_stock_count,
        'expiring_contracts': expiring_contracts_count
    })
