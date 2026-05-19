/**
 * НормаКорм — загальні JS утиліти
 */

// ===== Toast Notifications =====
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(16px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== Modal helpers =====
function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
    }
});

// ===== Format helpers =====
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return parseFloat(num).toFixed(decimals);
}

function formatCurrency(num) {
    if (num === null || num === undefined) return '-';
    return parseFloat(num).toFixed(2) + ' ₴';
}
