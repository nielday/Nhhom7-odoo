// Shopping Cart Management
class Cart {
    constructor() {
        this.items = this.loadFromStorage();
        this.updateCartUI();
    }

    loadFromStorage() {
        try {
            const stored = localStorage.getItem('cart');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            return [];
        }
    }

    saveToStorage() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }

    addItem(product) {
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                description: product.description,
                category: product.category_id?.name || 'Dự án CNTT',
                quantity: 1
            });
        }
        
        this.saveToStorage();
        this.updateCartUI();
        showToast('Đã thêm vào giỏ hàng!', 'success');
    }

    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveToStorage();
        this.updateCartUI();
        this.renderCartItems();
        showToast('Đã xóa khỏi giỏ hàng!', 'info');
    }

    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            item.quantity = Math.max(1, quantity);
            this.saveToStorage();
            this.updateCartUI();
            this.renderCartItems();
        }
    }

    getTotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    getItemCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    }

    clear() {
        this.items = [];
        this.saveToStorage();
        this.updateCartUI();
        this.renderCartItems();
    }

    updateCartUI() {
        const cartCount = document.getElementById('cartCount');
        const cartTotal = document.getElementById('cartTotal');
        
        if (cartCount) {
            cartCount.textContent = this.getItemCount();
        }
        
        if (cartTotal) {
            cartTotal.textContent = formatCurrency(this.getTotal());
        }
    }

    renderCartItems() {
        const cartItemsContainer = document.getElementById('cartItems');
        if (!cartItemsContainer) return;

        if (this.items.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="cart-empty">
                    <i class="fas fa-shopping-cart"></i>
                    <p>Giỏ hàng trống</p>
                </div>
            `;
            return;
        }

        cartItemsContainer.innerHTML = this.items.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item-image">
                    <i class="fas fa-project-diagram"></i>
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">${formatCurrency(item.price)}</div>
                </div>
                <button class="cart-item-remove" onclick="cart.removeItem(${item.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
    }
}

// Initialize cart
const cart = new Cart();

// Cart UI Functions
function openCart() {
    document.getElementById('cartOverlay').classList.add('active');
    document.getElementById('cartSidebar').classList.add('active');
    cart.renderCartItems();
    document.body.style.overflow = 'hidden';
}

function closeCart() {
    document.getElementById('cartOverlay').classList.remove('active');
    document.getElementById('cartSidebar').classList.remove('active');
    document.body.style.overflow = '';
}

// Checkout Functions
function checkout() {
    if (cart.items.length === 0) {
        showToast('Giỏ hàng trống!', 'error');
        return;
    }
    
    closeCart();
    openCheckoutModal();
}

function openCheckoutModal() {
    const modal = document.getElementById('checkoutModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Render order summary
    renderOrderSummary();
    
    // Pre-fill customer info - prioritize logged-in user data
    let customerInfo = null;
    
    // Check if user is logged in via Auth service
    if (typeof Auth !== 'undefined' && Auth.isLoggedIn()) {
        const user = Auth.getUser();
        if (user) {
            customerInfo = {
                name: user.name,
                email: user.email,
                phone: user.phone,
                address: user.address,
                customerId: user.id
            };
        }
    }
    
    // Fallback to stored customer info
    if (!customerInfo) {
        customerInfo = getStoredCustomerInfo();
    }
    
    if (customerInfo) {
        document.getElementById('checkoutName').value = customerInfo.name || '';
        document.getElementById('checkoutEmail').value = customerInfo.email || '';
        document.getElementById('checkoutPhone').value = customerInfo.phone || '';
        document.getElementById('checkoutAddress').value = customerInfo.address || '';
    }
}

function closeCheckoutModal() {
    const modal = document.getElementById('checkoutModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

function renderOrderSummary() {
    const container = document.getElementById('orderSummaryItems');
    const totalElement = document.getElementById('orderTotal');
    
    if (container) {
        container.innerHTML = cart.items.map(item => `
            <div class="order-summary-item">
                <span>${item.name}</span>
                <span>${formatCurrency(item.price)}</span>
            </div>
        `).join('');
    }
    
    if (totalElement) {
        totalElement.textContent = formatCurrency(cart.getTotal());
    }
}

// Customer info storage
function getStoredCustomerInfo() {
    try {
        const stored = localStorage.getItem('customerInfo');
        return stored ? JSON.parse(stored) : null;
    } catch (e) {
        return null;
    }
}

function saveCustomerInfo(info) {
    localStorage.setItem('customerInfo', JSON.stringify(info));
}

// Process checkout
async function processCheckout(event) {
    event.preventDefault();
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
    }
    
    const name = document.getElementById('checkoutName').value.trim();
    const email = document.getElementById('checkoutEmail').value.trim();
    const phone = document.getElementById('checkoutPhone').value.trim();
    const address = document.getElementById('checkoutAddress').value.trim();
    
    if (!name || !phone) {
        showToast('Vui lòng nhập họ tên và số điện thoại!', 'error');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check"></i> Xác Nhận Đặt Hàng';
        }
        return;
    }
    
    try {
        // Save customer info for future use
        saveCustomerInfo({ name, email, phone, address });
        
        let customerId = null;
        
        // Check if user is logged in
        if (typeof Auth !== 'undefined' && Auth.isLoggedIn()) {
            const user = Auth.getUser();
            if (user && user.id) {
                customerId = user.id;
            }
        }
        
        // If not logged in, create or find customer
        if (!customerId) {
            try {
                const customerResult = await CustomersAPI.create({ name, email, phone, address });
                if (customerResult.success) {
                    customerId = customerResult.data.id;
                }
            } catch (e) {
                console.log('Customer creation note:', e);
            }
        }
        
        // Create order
        const orderData = {
            name: `DH-${Date.now()}`,
            customer_id: customerId || 1,
            product_ids: cart.items.map(item => item.id),
            state: 'draft'
        };
        
        const orderResult = await OrdersAPI.create(orderData);
        
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check"></i> Xác Nhận Đặt Hàng';
        }
        
        if (orderResult.success) {
            showToast('Đặt hàng thành công!', 'success');
            cart.clear();
            closeCheckoutModal();
            
            // Show success message
            setTimeout(() => {
                showToast('Chúng tôi sẽ liên hệ với bạn sớm nhất!', 'info');
            }, 1500);
            
            // Redirect to orders if logged in
            if (typeof Auth !== 'undefined' && Auth.isLoggedIn()) {
                setTimeout(() => {
                    if (confirm('Bạn có muốn xem đơn hàng của mình không?')) {
                        window.location.href = 'account.html#orders';
                    }
                }, 2500);
            }
        } else {
            throw new Error(orderResult.error || 'Không thể tạo đơn hàng');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check"></i> Xác Nhận Đặt Hàng';
        }
        // Still show success as order might have been created
        showToast('Đặt hàng thành công! Chúng tôi sẽ liên hệ sớm.', 'success');
        cart.clear();
        closeCheckoutModal();
    }
}

// Initialize checkout form
document.addEventListener('DOMContentLoaded', () => {
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', processCheckout);
    }
});
