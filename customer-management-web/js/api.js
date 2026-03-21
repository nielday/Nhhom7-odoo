// API Service
class ApiService {
    constructor() {
        this.baseUrl = CONFIG.API_BASE_URL;
    }

    // GET request for HTTP type endpoints
    async get(endpoint) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    }

    // POST request for JSON type endpoints
    async post(endpoint, data = {}) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Handle Odoo type='json' response (wrapped in 'result' key)
            if (result.error) {
                throw new Error(result.error.data?.message || result.error.message || 'Unknown error');
            }
            
            return result.result !== undefined ? result.result : result;
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }
}

// API instance
const api = new ApiService();

// Products API - Used in main.js and products.js
const ProductsAPI = {
    async getAll() {
        return await api.get(CONFIG.ENDPOINTS.PRODUCTS);
    }
};

// Categories API - Used in main.js
const CategoriesAPI = {
    async getAll() {
        return await api.get(CONFIG.ENDPOINTS.PRODUCT_CATEGORIES);
    }
};

// Customers API - Used in cart.js
const CustomersAPI = {
    async create(data) {
        return await api.post(CONFIG.ENDPOINTS.CUSTOMERS, data);
    }
};

// Orders API - Used in cart.js
const OrdersAPI = {
    async create(data) {
        return await api.post(CONFIG.ENDPOINTS.ORDERS, data);
    }
};

// Feedbacks API - Used in contact.html
const FeedbacksAPI = {
    async create(data) {
        return await api.post(CONFIG.ENDPOINTS.FEEDBACKS, data);
    }
};
