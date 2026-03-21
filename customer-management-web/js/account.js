// Account Page JavaScript

document.addEventListener('DOMContentLoaded', () => {
    initAccountPage();
});

// Initialize account page
async function initAccountPage() {
    // Check if user is logged in
    if (!Auth.isLoggedIn()) {
        window.location.href = 'index.html';
        showToast('Vui lòng đăng nhập để tiếp tục!', 'warning');
        return;
    }

    // Verify token
    const isValid = await Auth.verifyToken();
    if (!isValid) {
        window.location.href = 'index.html';
        showToast('Phiên đăng nhập đã hết hạn!', 'warning');
        return;
    }

    // Load user profile
    await loadProfile();

    // Setup forms
    setupProfileForm();
    setupPasswordForm();

    // Check URL hash for tab
    const hash = window.location.hash.replace('#', '');
    if (hash && ['profile', 'orders', 'settings'].includes(hash)) {
        const tab = document.querySelector(`[onclick*="switchTab('${hash}'"]`);
        if (tab) switchTab(hash, tab);
    }

    // Update UI
    updateAuthUI();
}

// Load user profile
async function loadProfile() {
    const result = await Auth.getProfile();
    
    if (result.success) {
        const user = result.data;
        
        // Update sidebar
        document.getElementById('accountUserName').textContent = user.name;
        document.getElementById('accountUsername').textContent = '@' + user.username;
        
        // Update profile form
        document.getElementById('profileName').value = user.name || '';
        document.getElementById('profileUsername').value = user.username || '';
        document.getElementById('profileEmail').value = user.email || '';
        document.getElementById('profilePhone').value = user.phone || '';
        document.getElementById('profileAddress').value = user.address || '';
    } else {
        showToast('Không thể tải thông tin tài khoản!', 'error');
    }
}

// Load orders
async function loadOrders() {
    const container = document.getElementById('ordersList');
    if (!container) return;

    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Đang tải đơn hàng...</p>
        </div>
    `;

    const result = await Auth.getMyOrders();
    
    if (result.success) {
        const orders = result.data;
        
        if (orders.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-shopping-bag"></i>
                    <h3>Chưa có đơn hàng nào</h3>
                    <p>Hãy khám phá sản phẩm và đặt hàng ngay!</p>
                    <a href="products.html" class="btn btn-primary">
                        <i class="fas fa-shopping-cart"></i>
                        Mua sắm ngay
                    </a>
                </div>
            `;
            return;
        }

        container.innerHTML = orders.map(order => `
            <div class="order-item">
                <div class="order-header">
                    <div class="order-info">
                        <h4>${order.name}</h4>
                        <span class="order-date">
                            <i class="fas fa-calendar"></i>
                            ${formatDate(order.date_order)}
                        </span>
                    </div>
                    <span class="order-status ${getStatusClass(order.state)}">
                        ${getStatusText(order.state)}
                    </span>
                </div>
                <div class="order-products">
                    ${order.products.map(p => `
                        <div class="order-product">
                            <span class="product-name">${p.name}</span>
                            <span class="product-price">${formatPrice(p.price)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="order-footer">
                    <div class="order-delivery" ${order.delivery_date ? '' : 'style="visibility:hidden"'}>
                        <i class="fas fa-truck"></i>
                        Dự kiến giao: ${order.delivery_date ? formatDate(order.delivery_date) : 'N/A'}
                    </div>
                    <div class="order-total">
                        Tổng: <strong>${formatPrice(order.total_amount)}</strong>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        container.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Không thể tải đơn hàng. Vui lòng thử lại!</p>
            </div>
        `;
    }
}

// Setup profile form
function setupProfileForm() {
    const form = document.getElementById('profileForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';

        const data = {
            name: document.getElementById('profileName').value.trim(),
            email: document.getElementById('profileEmail').value.trim(),
            phone: document.getElementById('profilePhone').value.trim(),
            address: document.getElementById('profileAddress').value.trim()
        };

        const result = await Auth.updateProfile(data);

        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-save"></i> Lưu thay đổi';

        if (result.success) {
            showToast('Cập nhật thông tin thành công!', 'success');
            document.getElementById('accountUserName').textContent = data.name;
            updateAuthUI();
        } else {
            showToast(result.error || 'Có lỗi xảy ra!', 'error');
        }
    });
}

// Setup password form
function setupPasswordForm() {
    const form = document.getElementById('passwordForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmNewPassword').value;

        if (newPassword !== confirmPassword) {
            showToast('Mật khẩu xác nhận không khớp!', 'error');
            return;
        }

        if (newPassword.length < 6) {
            showToast('Mật khẩu mới phải có ít nhất 6 ký tự!', 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';

        const result = await Auth.changePassword(currentPassword, newPassword);
        console.log(result);

        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-key"></i> Đổi mật khẩu';

        if (result.success) {
            showToast('Đổi mật khẩu thành công! Vui lòng đăng nhập lại.', 'success');
            form.reset();
            
            // Logout and redirect after 2 seconds
            setTimeout(() => {
                Auth.logout();
                window.location.href = 'index.html';
            }, 2000);
        } else {
            showToast(result.error || 'Có lỗi xảy ra!', 'error');
        }
    });
}

// Switch tab
function switchTab(tabName, element) {
    // Update nav items
    document.querySelectorAll('.account-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    if (element) element.classList.add('active');

    // Update tabs
    document.querySelectorAll('.account-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    const targetTab = document.getElementById(tabName + 'Tab');
    if (targetTab) {
        targetTab.classList.add('active');
    }

    // Load orders if switching to orders tab
    if (tabName === 'orders') {
        loadOrders();
    }

    // Update URL hash
    window.history.replaceState(null, null, '#' + tabName);
}

// Toggle password visibility
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.parentElement.querySelector('.toggle-password i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Handle logout
function handleLogout() {
    Auth.logout();
    window.location.href = 'index.html';
}

// Helper functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price);
}

function getStatusClass(state) {
    const classes = {
        'draft': 'status-draft',
        'confirmed': 'status-confirmed',
        'shipping': 'status-shipping',
        'done': 'status-done',
        'cancel': 'status-cancelled'
    };
    return classes[state] || 'status-default';
}

function getStatusText(state) {
    const texts = {
        'draft': 'Chờ xác nhận',
        'confirmed': 'Đã xác nhận',
        'shipping': 'Đang giao',
        'done': 'Hoàn thành',
        'cancel': 'Đã hủy'
    };
    return texts[state] || state;
}
