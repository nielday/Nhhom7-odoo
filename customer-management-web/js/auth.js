// Authentication Service
class AuthService {
    constructor() {
        this.baseUrl = CONFIG.API_BASE_URL;
        this.tokenKey = 'customer_token';
        this.userKey = 'customer_user';
    }

    // Get stored token
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    // Get stored user
    getUser() {
        const user = localStorage.getItem(this.userKey);
        return user ? JSON.parse(user) : null;
    }

    // Check if user is logged in
    isLoggedIn() {
        return !!this.getToken();
    }

    // Save auth data
    saveAuth(token, user) {
        localStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    // Clear auth data
    clearAuth() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    // API request for Odoo type='json' endpoints
    async authRequest(endpoint, data = null) {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(this.baseUrl + endpoint, {
            method: 'POST',
            headers,
            body: JSON.stringify(data || {})
        });
        
        const result = await response.json();
        
        // Odoo type='json' wraps response in 'result' key
        if (result.error) {
            return { 
                success: false, 
                error: result.error.data?.message || result.error.message || 'Có lỗi xảy ra' 
            };
        }
        
        return result.result || result;
    }

    // Register new customer
    async register(userData) {
        try {
            const result = await this.authRequest('/api/auth/register', userData);
            
            if (result.success) {
                this.saveAuth(result.data.token, result.data.customer);
            }
            
            return result;
        } catch (error) {
            console.error('Register error:', error);
            return { success: false, error: error.message };
        }
    }

    // Login
    async login(username, password) {
        try {
            const result = await this.authRequest('/api/auth/login', { username, password });
            
            if (result.success) {
                this.saveAuth(result.data.token, result.data.customer);
            }
            
            return result;
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    }

    // Logout
    logout() {
        this.clearAuth();
    }

    // Get profile
    async getProfile() {
        try {
            return await this.authRequest('/api/auth/me', {});
        } catch (error) {
            console.error('Get profile error:', error);
            return { success: false, error: error.message };
        }
    }

    // Update profile
    async updateProfile(data) {
        try {
            const result = await this.authRequest('/api/auth/update-profile', data);
            
            if (result.success) {
                // Update stored user data
                const currentUser = this.getUser();
                const updatedUser = { ...currentUser, ...result.data };
                localStorage.setItem(this.userKey, JSON.stringify(updatedUser));
            }
            
            return result;
        } catch (error) {
            console.error('Update profile error:', error);
            return { success: false, error: error.message };
        }
    }

    // Change password
    async changePassword(oldPassword, newPassword) {
        try {
            return await this.authRequest('/api/auth/change-password', {
                old_password: oldPassword,
                new_password: newPassword
            });
        } catch (error) {
            console.error('Change password error:', error);
            return { success: false, error: error.message };
        }
    }

    // Get my orders
    async getMyOrders() {
        try {
            return await this.authRequest('/api/auth/my-orders', {});
        } catch (error) {
            console.error('Get orders error:', error);
            return { success: false, error: error.message };
        }
    }

    // Verify token
    async verifyToken() {
        try {
            const result = await this.authRequest('/api/auth/verify', {});
            if (!result.success || !result.valid) {
                this.clearAuth();
                return false;
            }
            return true;
        } catch (error) {
            this.clearAuth();
            return false;
        }
    }
}

// Global auth instance
const Auth = new AuthService();

// Update UI based on auth state
function updateAuthUI() {
    const user = Auth.getUser();
    const userBtn = document.getElementById('userBtn') || document.querySelector('.user-btn');
    const headerActions = document.querySelector('.header-actions');
    
    // Remove existing dropdown first
    const existingDropdown = document.getElementById('userDropdown');
    if (existingDropdown) {
        existingDropdown.remove();
    }
    
    if (user && Auth.isLoggedIn()) {
        // User is logged in
        if (userBtn) {
            userBtn.innerHTML = `
                <i class="fas fa-user-circle"></i>
                <span class="user-name">${user.name.split(' ')[0]}</span>
            `;
            userBtn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleUserMenu();
            };
        }
        
        // Add user dropdown
        if (headerActions) {
            const dropdown = document.createElement('div');
            dropdown.id = 'userDropdown';
            dropdown.className = 'user-dropdown';
            dropdown.innerHTML = `
                <div class="dropdown-header">
                    <i class="fas fa-user-circle"></i>
                    <div>
                        <strong>${user.name}</strong>
                        <small>@${user.username}</small>
                    </div>
                </div>
                <div class="dropdown-divider"></div>
                <a href="account.html" class="dropdown-item">
                    <i class="fas fa-user"></i> Tài khoản của tôi
                </a>
                <a href="account.html#orders" class="dropdown-item">
                    <i class="fas fa-shopping-bag"></i> Đơn hàng của tôi
                </a>
                <a href="account.html#settings" class="dropdown-item">
                    <i class="fas fa-cog"></i> Đổi mật khẩu
                </a>
                <div class="dropdown-divider"></div>
                <a href="#" class="dropdown-item text-danger" id="logoutBtn">
                    <i class="fas fa-sign-out-alt"></i> Đăng xuất
                </a>
            `;
            headerActions.appendChild(dropdown);
            
            // Add logout handler
            document.getElementById('logoutBtn').addEventListener('click', function(e) {
                e.preventDefault();
                handleLogout();
            });
        }
    } else {
        // User is not logged in
        if (userBtn) {
            userBtn.innerHTML = '<i class="fas fa-user"></i>';
            userBtn.onclick = function(e) {
                e.preventDefault();
                openAuthModal();
            };
        }
    }
}

// Handle logout
function handleLogout() {
    Auth.clearAuth();
    updateAuthUI();
    showToast('Đăng xuất thành công!', 'success');
    
    // Redirect to home if on account page
    if (window.location.pathname.includes('account.html')) {
        window.location.href = 'index.html';
    }
}

// Toggle user dropdown menu
function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown && !e.target.closest('.user-btn') && !e.target.closest('.user-dropdown')) {
        dropdown.classList.remove('show');
    }
});

// Auth Modal Functions
let isLoginMode = true;

function openAuthModal() {
    if (Auth.isLoggedIn()) {
        window.location.href = 'account.html';
        return;
    }
    
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.add('active');
        isLoginMode = true;
        updateAuthModalUI();
    }
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.remove('active');
        // Reset form
        const form = document.getElementById('authForm');
        if (form) form.reset();
    }
}

function toggleAuthMode(e) {
    if (e) e.preventDefault();
    isLoginMode = !isLoginMode;
    updateAuthModalUI();
}

function updateAuthModalUI() {
    const title = document.getElementById('authModalTitle');
    const btnText = document.getElementById('authBtnText');
    const switchText = document.getElementById('authSwitchText');
    const switchLink = document.querySelector('.auth-switch a');
    const nameGroup = document.getElementById('nameGroup');
    const phoneGroup = document.getElementById('phoneGroup');
    const emailGroup = document.getElementById('emailGroup');
    const usernameGroup = document.getElementById('usernameGroup');
    const passwordGroup = document.getElementById('passwordGroup');
    const confirmPasswordGroup = document.getElementById('confirmPasswordGroup');
    
    if (isLoginMode) {
        if (title) title.textContent = 'Đăng Nhập';
        if (btnText) btnText.textContent = 'Đăng Nhập';
        if (switchText) switchText.textContent = 'Chưa có tài khoản?';
        if (switchLink) switchLink.textContent = 'Đăng ký';
        if (nameGroup) nameGroup.style.display = 'none';
        if (phoneGroup) phoneGroup.style.display = 'none';
        if (emailGroup) emailGroup.style.display = 'none';
        if (confirmPasswordGroup) confirmPasswordGroup.style.display = 'none';
    } else {
        if (title) title.textContent = 'Đăng Ký';
        if (btnText) btnText.textContent = 'Đăng Ký';
        if (switchText) switchText.textContent = 'Đã có tài khoản?';
        if (switchLink) switchLink.textContent = 'Đăng nhập';
        if (nameGroup) nameGroup.style.display = 'block';
        if (phoneGroup) phoneGroup.style.display = 'block';
        if (emailGroup) emailGroup.style.display = 'block';
        if (confirmPasswordGroup) confirmPasswordGroup.style.display = 'block';
    }
}

// Handle auth form submission
async function handleAuthSubmit(e) {
    e.preventDefault();
    
    const username = document.getElementById('authUsername')?.value?.trim();
    const password = document.getElementById('authPassword')?.value;
    const btnText = document.getElementById('authBtnText');
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!username || !password) {
        showToast('Vui lòng nhập đầy đủ thông tin!', 'error');
        return;
    }
    
    // Disable button
    if (submitBtn) submitBtn.disabled = true;
    if (btnText) btnText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
    
    let result;
    
    if (isLoginMode) {
        // Login
        result = await Auth.login(username, password);
    } else {
        // Register
        const name = document.getElementById('authName')?.value?.trim();
        const email = document.getElementById('authEmail')?.value?.trim();
        const phone = document.getElementById('authPhone')?.value?.trim();
        const confirmPassword = document.getElementById('authConfirmPassword')?.value;
        
        if (!name) {
            showToast('Vui lòng nhập họ và tên!', 'error');
            if (submitBtn) submitBtn.disabled = false;
            if (btnText) btnText.textContent = 'Đăng Ký';
            return;
        }
        
        if (password !== confirmPassword) {
            showToast('Mật khẩu xác nhận không khớp!', 'error');
            if (submitBtn) submitBtn.disabled = false;
            if (btnText) btnText.textContent = 'Đăng Ký';
            return;
        }
        
        result = await Auth.register({
            username,
            password,
            name,
            email,
            phone
        });
    }
    
    // Enable button
    if (submitBtn) submitBtn.disabled = false;
    if (btnText) btnText.textContent = isLoginMode ? 'Đăng Nhập' : 'Đăng Ký';
    
    if (result.success) {
        showToast(result.message || (isLoginMode ? 'Đăng nhập thành công!' : 'Đăng ký thành công!'), 'success');
        closeAuthModal();
        updateAuthUI();
    } else {
        showToast(result.error || 'Có lỗi xảy ra!', 'error');
    }
}

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check token validity
    if (Auth.isLoggedIn()) {
        Auth.verifyToken().then(valid => {
            if (valid) {
                updateAuthUI();
            }
        });
    }
    
    // Setup auth form
    const authForm = document.getElementById('authForm');
    if (authForm) {
        authForm.addEventListener('submit', handleAuthSubmit);
    }
    
    updateAuthUI();
});
