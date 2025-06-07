"""
ملف JavaScript لتطبيق aljeel alhadith elevator
"""

// تبديل حالة الشريط الجانبي
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // إغلاق التنبيهات تلقائياً
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // جعل صفوف الجداول قابلة للنقر
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            window.location.href = this.dataset.href;
        });
    });
    
    // تفعيل tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // تفعيل popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // تأكيد الحذف
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('هل أنت متأكد من رغبتك في الحذف؟')) {
                e.preventDefault();
            }
        });
    });
    
    // معاينة الصور قبل الرفع
    const imageInputs = document.querySelectorAll('.image-input');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const preview = document.getElementById(this.dataset.preview);
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // تحديث حقول التاريخ والوقت
    const dateTimeFields = document.querySelectorAll('.datetime-field');
    dateTimeFields.forEach(function(field) {
        if (field.dataset.value) {
            field.value = field.dataset.value;
        }
    });
    
    // تفعيل مربعات البحث المباشر
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        input.addEventListener('keyup', function() {
            const searchValue = this.value.toLowerCase();
            const targetTable = document.getElementById(this.dataset.target);
            if (targetTable) {
                const rows = targetTable.querySelectorAll('tbody tr');
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchValue)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });
    
    // تفعيل الفرز في الجداول
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            const isAscending = this.classList.contains('asc');
            
            // تحديث حالة الفرز
            sortableHeaders.forEach(h => h.classList.remove('asc', 'desc'));
            this.classList.add(isAscending ? 'desc' : 'asc');
            
            // فرز الصفوف
            rows.sort(function(a, b) {
                const cellA = a.children[columnIndex].textContent.trim();
                const cellB = b.children[columnIndex].textContent.trim();
                
                if (!isNaN(cellA) && !isNaN(cellB)) {
                    return isAscending ? cellA - cellB : cellB - cellA;
                } else {
                    return isAscending ? 
                        cellA.localeCompare(cellB, 'ar') : 
                        cellB.localeCompare(cellA, 'ar');
                }
            });
            
            // إعادة ترتيب الصفوف
            const tbody = table.querySelector('tbody');
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });
        });
    });
});
