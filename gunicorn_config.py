"""
ملف إعدادات Gunicorn للنشر في بيئة الإنتاج
"""
import multiprocessing

# عدد العمليات المتزامنة
# تم تعديل عدد العمليات إلى 1 لتجنب مشكلة قفل قاعدة بيانات SQLite
workers = 1

# المنفذ الذي سيستمع عليه التطبيق
bind = "0.0.0.0:5000"

# وضع التشغيل
worker_class = "sync"

# مستوى السجلات
loglevel = "info"

# ملف السجلات
accesslog = "/home/ubuntu/aljeel_alhadith_elevator_web/logs/access.log"
errorlog = "/home/ubuntu/aljeel_alhadith_elevator_web/logs/error.log"

# وقت انتظار العمليات
timeout = 120

# إعادة تشغيل العمليات بعد عدد معين من الطلبات
max_requests = 1000
max_requests_jitter = 50

# تفعيل وضع daemon
daemon = True
