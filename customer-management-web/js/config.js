// API Configuration
const CONFIG = {
    // API Base URL - Using proxy server (no need to specify port, same as frontend)
    API_BASE_URL: '',
    
    // API Endpoints - Only used endpoints
    ENDPOINTS: {
        // Customers
        CUSTOMERS: '/api/customers',
        
        // Products
        PRODUCTS: '/api/products',
        
        // Product Categories
        PRODUCT_CATEGORIES: '/api/product-categories',
        
        // Orders
        ORDERS: '/api/orders',
        
        // Feedbacks
        FEEDBACKS: '/api/feedbacks'
    },
    
    // Currency settings
    CURRENCY: {
        symbol: '₫',
        locale: 'vi-VN'
    },
    
    // Default pagination
    PAGINATION: {
        defaultLimit: 12,
        maxLimit: 50
    }
};

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat(CONFIG.CURRENCY.locale, {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount) + ' ' + CONFIG.CURRENCY.symbol;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}
