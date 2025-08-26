// الوظائف الرئيسية للنظام
$(document).ready(function() {
    // تهيئة التطبيق
    initializeApp();

    // تهيئة الأحداث
    bindEvents();

    // تحديث الوقت
    updateDateTime();
    setInterval(updateDateTime, 1000);

    // تهيئة القائمة الجانبية
    initSidebar();

    // تحديث التاريخ والوقت في الشريط العلوي
    updateHeaderDateTime();
    setInterval(updateHeaderDateTime, 1000);
});

// تهيئة التطبيق
function initializeApp() {
    // تهيئة التلميحات
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // تهيئة النوافذ المنبثقة
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // تهيئة الجداول القابلة للفرز
    if (typeof DataTable !== 'undefined') {
        $('.data-table').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/ar.json'
            },
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']]
        });
    }
    
    // تحقق من حالة الاتصال
    checkConnectionStatus();
}

// ربط الأحداث
function bindEvents() {
    // تأكيد الحذف
    $(document).on('click', '.delete-btn', function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        const itemName = $(this).data('item-name') || 'هذا العنصر';
        
        showConfirmDialog(
            'تأكيد الحذف',
            `هل أنت متأكد من حذف ${itemName}؟ لا يمكن التراجع عن هذا الإجراء.`,
            'حذف',
            'إلغاء',
            function() {
                window.location.href = url;
            }
        );
    });
    
    // البحث السريع
    $('#quickSearch').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        $('.searchable-item').each(function() {
            const text = $(this).text().toLowerCase();
            $(this).toggle(text.includes(searchTerm));
        });
    });
    
    // تحديث تلقائي للإحصائيات
    if ($('#dashboard').length) {
        setInterval(updateDashboardStats, 30000); // كل 30 ثانية
    }
    
    // حفظ تلقائي للنماذج
    $('form.auto-save').on('input change', debounce(autoSaveForm, 2000));
    
    // تحديد الكل في الجداول
    $('.select-all').on('change', function() {
        const isChecked = $(this).is(':checked');
        $(this).closest('table').find('.select-item').prop('checked', isChecked);
        updateBulkActions();
    });
    
    $('.select-item').on('change', function() {
        updateBulkActions();
    });
}

// تحديث التاريخ والوقت
function updateDateTime() {
    const now = new Date();
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Africa/Cairo'
    };
    
    const dateTimeString = now.toLocaleDateString('ar-EG', options);
    $('#current-datetime').text(dateTimeString);
}

// عرض رسائل التنبيه
function showAlert(message, type = 'info', duration = 5000) {
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('#alerts-container').append(alertHtml);
    
    // إزالة التنبيه تلقائياً
    setTimeout(() => {
        $(`#${alertId}`).alert('close');
    }, duration);
}

// عرض نافذة تأكيد
function showConfirmDialog(title, message, confirmText, cancelText, onConfirm) {
    const modalHtml = `
        <div class="modal fade" id="confirmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                        <button type="button" class="btn btn-danger" id="confirmAction">${confirmText}</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // إزالة النافذة السابقة إن وجدت
    $('#confirmModal').remove();
    
    // إضافة النافذة الجديدة
    $('body').append(modalHtml);
    
    // عرض النافذة
    const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
    modal.show();
    
    // ربط حدث التأكيد
    $('#confirmAction').on('click', function() {
        modal.hide();
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    });
    
    // إزالة النافذة عند الإغلاق
    $('#confirmModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// تحديث إحصائيات لوحة التحكم
function updateDashboardStats() {
    $.ajax({
        url: '/api/dashboard-stats',
        method: 'GET',
        success: function(data) {
            $('#total-products').text(data.total_products);
            $('#low-stock-products').text(data.low_stock_products);
            $('#today-sales').text(data.today_sales);
            $('#today-revenue').text(data.today_revenue.toFixed(2) + ' ج.م');
        },
        error: function() {
            console.log('فشل في تحديث الإحصائيات');
        }
    });
}

// حفظ تلقائي للنماذج
function autoSaveForm() {
    const form = $(this);
    const formData = form.serialize();
    
    $.ajax({
        url: form.attr('action') || window.location.href,
        method: 'POST',
        data: formData + '&auto_save=1',
        success: function() {
            showAlert('تم الحفظ تلقائياً', 'success', 2000);
        },
        error: function() {
            showAlert('فشل في الحفظ التلقائي', 'warning', 3000);
        }
    });
}

// تحديث إجراءات الدفعة
function updateBulkActions() {
    const selectedItems = $('.select-item:checked').length;
    const bulkActions = $('.bulk-actions');
    
    if (selectedItems > 0) {
        bulkActions.removeClass('d-none');
        $('.selected-count').text(selectedItems);
    } else {
        bulkActions.addClass('d-none');
    }
}

// تحقق من حالة الاتصال
function checkConnectionStatus() {
    function updateOnlineStatus() {
        const status = navigator.onLine ? 'متصل' : 'غير متصل';
        const statusClass = navigator.onLine ? 'text-success' : 'text-danger';
        $('#connection-status').removeClass('text-success text-danger').addClass(statusClass).text(status);
        
        if (!navigator.onLine) {
            showAlert('تم فقدان الاتصال بالإنترنت. بعض الميزات قد لا تعمل بشكل صحيح.', 'warning');
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
}

// دالة التأخير (Debounce)
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// تنسيق الأرقام
function formatNumber(num) {
    return new Intl.NumberFormat('ar-EG').format(num);
}

// تنسيق العملة
function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-EG', {
        style: 'currency',
        currency: 'EGP'
    }).format(amount);
}

// طباعة الصفحة
function printPage() {
    window.print();
}

// تصدير البيانات
function exportData(format, url) {
    const link = document.createElement('a');
    link.href = url + '?format=' + format;
    link.download = 'export.' + format;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// تحميل البيانات بـ AJAX
function loadData(url, container, showLoading = true) {
    if (showLoading) {
        $(container).html('<div class="text-center p-4"><div class="loading-spinner"></div></div>');
    }
    
    $.ajax({
        url: url,
        method: 'GET',
        success: function(data) {
            $(container).html(data);
        },
        error: function() {
            $(container).html('<div class="alert alert-danger">فشل في تحميل البيانات</div>');
        }
    });
}

// التحقق من صحة النماذج
function validateForm(form) {
    let isValid = true;
    
    $(form).find('[required]').each(function() {
        const field = $(this);
        const value = field.val().trim();
        
        if (!value) {
            field.addClass('is-invalid');
            isValid = false;
        } else {
            field.removeClass('is-invalid');
        }
    });
    
    return isValid;
}

// إعدادات عامة
const AppSettings = {
    currency: 'EGP',
    locale: 'ar-EG',
    dateFormat: 'DD/MM/YYYY',
    timeFormat: 'HH:mm:ss'
};

// تحديث التاريخ والوقت في الشريط العلوي
function updateHeaderDateTime() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };

    const arabicDateTime = now.toLocaleDateString('ar-EG', options);
    const datetimeElement = document.getElementById('current-datetime');
    if (datetimeElement) {
        datetimeElement.textContent = arabicDateTime;
    }
}

// تهيئة القائمة الجانبية
function initSidebar() {
    // التحكم في القوائم الفرعية
    document.querySelectorAll('.has-submenu > .nav-link').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const parent = this.parentElement;
            const isOpen = parent.classList.contains('open');

            // إغلاق جميع القوائم الفرعية الأخرى
            document.querySelectorAll('.has-submenu.open').forEach(function(item) {
                if (item !== parent) {
                    item.classList.remove('open');
                }
            });

            // تبديل حالة القائمة الحالية
            parent.classList.toggle('open', !isOpen);
        });
    });

    // زر إخفاء/إظهار القائمة الجانبية
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('show');
                overlay.classList.toggle('show');
            }
        });
    }

    // إغلاق القائمة عند النقر على الخلفية
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // تحديث الرابط النشط
    updateActiveNavLink();
}

// تحديث الرابط النشط في القائمة
function updateActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(function(link) {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// إظهار نافذة إضافة منتج
function showAddProductModal() {
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(document.getElementById('addProductModal'));
        modal.show();
    }
}

// تفعيل الروابط النشطة
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .submenu-link');

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            // فتح القائمة الفرعية إذا كان الرابط فيها
            const parentSubmenu = link.closest('.has-submenu');
            if (parentSubmenu) {
                parentSubmenu.classList.add('open');
            }
        }
    });
}

// تصدير الوظائف للاستخدام العام
window.SupermarketApp = {
    showAlert,
    showConfirmDialog,
    formatNumber,
    formatCurrency,
    printPage,
    exportData,
    loadData,
    validateForm,
    initSidebar,
    updateHeaderDateTime,
    updateActiveNavLink,
    showAddProductModal,
    setActiveNavLink,
    settings: AppSettings
};
