// Products Page JavaScript

let allProducts = [];
let allCategories = [];
let currentFilter = 'all';
let currentCategoryParam = null;

// Category descriptions for hero banner
const CATEGORY_INFO = {
    'Website': {
        desc: 'Giải pháp website chuyên nghiệp, responsive, tối ưu SEO — từ landing page đến hệ thống web phức tạp.',
        gradient: 'linear-gradient(135deg, #667eea, #764ba2)'
    },
    'E-Commerce': {
        desc: 'Nền tảng thương mại điện tử toàn diện với giỏ hàng, thanh toán online, quản lý đơn hàng và kho.',
        gradient: 'linear-gradient(135deg, #f093fb, #f5576c)'
    },
    'Mobile App': {
        desc: 'Ứng dụng di động đa nền tảng iOS/Android với UI/UX hiện đại, hiệu năng cao.',
        gradient: 'linear-gradient(135deg, #4facfe, #00f2fe)'
    },
    'ERP': {
        desc: 'Hệ thống quản lý doanh nghiệp tổng thể: nhân sự, kế toán, kho, sản xuất, dự án.',
        gradient: 'linear-gradient(135deg, #43e97b, #38f9d7)'
    },
    'CRM': {
        desc: 'Phần mềm quản lý quan hệ khách hàng, tự động hóa bán hàng và chăm sóc khách hàng.',
        gradient: 'linear-gradient(135deg, #fa709a, #fee140)'
    },
    'Booking': {
        desc: 'Giải pháp đặt lịch hẹn online cho spa, salon, phòng khám và các dịch vụ.',
        gradient: 'linear-gradient(135deg, #a18cd1, #fbc2eb)'
    },
    'API': {
        desc: 'Xây dựng và tích hợp API RESTful, GraphQL cho hệ thống backend hiện đại.',
        gradient: 'linear-gradient(135deg, #fccb90, #d57eeb)'
    },
    'AI/ML': {
        desc: 'Ứng dụng trí tuệ nhân tạo và machine learning vào sản phẩm thực tế.',
        gradient: 'linear-gradient(135deg, #667eea, #764ba2)'
    },
    'Cloud': {
        desc: 'Dịch vụ cloud, DevOps, triển khai và quản lý hạ tầng đám mây.',
        gradient: 'linear-gradient(135deg, #89f7fe, #66a6ff)'
    }
};

// Get category gradient
function getCategoryGradient(category) {
    return CATEGORY_INFO[category]?.gradient || 'linear-gradient(135deg, #667eea, #764ba2)';
}

// Initialize Products Page
document.addEventListener('DOMContentLoaded', () => {
    currentCategoryParam = new URLSearchParams(window.location.search).get('category');
    loadAllProducts();
    loadFilterCategories();
});

// Load All Products
async function loadAllProducts() {
    const container = document.getElementById('productsGrid');
    if (!container) return;

    try {
        const response = await ProductsAPI.getAll();

        if (response.success && response.data && response.data.length > 0) {
            allProducts = response.data;
        } else {
            allProducts = getDemoProducts();
        }
    } catch (error) {
        console.error('Error loading products:', error);
        allProducts = getDemoProducts();
    }

    // If category param exists, show category UI and filter
    if (currentCategoryParam && currentCategoryParam !== 'all') {
        showCategoryHero(currentCategoryParam);
        filterProducts(currentCategoryParam);
    } else {
        renderProductsGrid(allProducts);
    }

    updateCategoryCounts();
}

// Load filter categories from API
async function loadFilterCategories() {
    const container = document.getElementById('filterButtons');
    if (!container) return;

    try {
        const response = await CategoriesAPI.getAll();

        if (response.success && response.data && response.data.length > 0) {
            allCategories = response.data;
            renderFilterButtons(container, response.data);
        } else {
            allCategories = getDefaultCategories();
            renderFilterButtons(container, allCategories);
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        allCategories = getDefaultCategories();
        renderFilterButtons(container, allCategories);
    }

    // Show related categories if viewing a specific category
    if (currentCategoryParam && currentCategoryParam !== 'all') {
        showRelatedCategories(currentCategoryParam);
    }
}

// Default categories fallback
function getDefaultCategories() {
    return [
        { name: 'Website' },
        { name: 'Mobile App' },
        { name: 'E-Commerce' },
        { name: 'ERP' },
        { name: 'CRM' }
    ];
}

// ========================================
// CATEGORY HERO BANNER
// ========================================
function showCategoryHero(category) {
    // Hide default header, show category hero
    const defaultHeader = document.getElementById('defaultPageHeader');
    const heroSection = document.getElementById('categoryHero');
    if (defaultHeader) defaultHeader.style.display = 'none';
    if (!heroSection) return;

    heroSection.style.display = 'block';
    heroSection.style.background = getCategoryGradient(category);

    // Breadcrumb
    const breadcrumb = document.getElementById('categoryBreadcrumb');
    if (breadcrumb) {
        breadcrumb.innerHTML = `
            <a href="index.html">Trang chủ</a>
            <span class="breadcrumb-sep"><i class="fas fa-chevron-right"></i></span>
            <a href="products.html">Dự án</a>
            <span class="breadcrumb-sep"><i class="fas fa-chevron-right"></i></span>
            <span class="breadcrumb-current">${category}</span>
        `;
    }

    // Icon
    const iconEl = document.getElementById('categoryHeroIcon');
    if (iconEl) {
        iconEl.innerHTML = `<i class="${getProductIcon(category)}"></i>`;
    }

    // Title
    const titleEl = document.getElementById('categoryHeroTitle');
    if (titleEl) {
        titleEl.textContent = category;
    }

    // Description
    const descEl = document.getElementById('categoryHeroDesc');
    if (descEl) {
        descEl.textContent = CATEGORY_INFO[category]?.desc || 'Khám phá các dự án trong danh mục này.';
    }

    // Stats
    const statsEl = document.getElementById('categoryHeroStats');
    if (statsEl) {
        const categoryProducts = allProducts.filter(p =>
            (p.category_id?.name || '').toLowerCase() === category.toLowerCase()
        );
        const count = categoryProducts.length;
        const prices = categoryProducts.map(p => p.price).filter(p => p > 0);
        const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
        const maxPrice = prices.length > 0 ? Math.max(...prices) : 0;

        statsEl.innerHTML = `
            <div class="hero-stat">
                <i class="fas fa-box"></i>
                <span>${count} dự án</span>
            </div>
            ${prices.length > 0 ? `
            <div class="hero-stat">
                <i class="fas fa-tag"></i>
                <span>Từ ${formatCurrency(minPrice)}</span>
            </div>
            <div class="hero-stat">
                <i class="fas fa-arrow-up"></i>
                <span>Đến ${formatCurrency(maxPrice)}</span>
            </div>
            ` : ''}
        `;
    }

    // Auto-activate the matching filter button after they load
    setTimeout(() => {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.textContent.trim().startsWith(category)) {
                btn.classList.add('active');
            }
        });
    }, 300);
}

// ========================================
// RELATED CATEGORIES
// ========================================
function showRelatedCategories(currentCategory) {
    const section = document.getElementById('relatedCategories');
    const grid = document.getElementById('relatedCategoriesGrid');
    if (!section || !grid) return;

    const related = allCategories.filter(c => c.name !== currentCategory);
    if (related.length === 0) return;

    section.style.display = 'block';

    grid.innerHTML = related.map(cat => {
        const count = allProducts.filter(p =>
            (p.category_id?.name || '').toLowerCase() === cat.name.toLowerCase()
        ).length;
        const countText = count > 0 ? count + ' dự án' : 'Xem dự án';

        return `
        <a href="products.html?category=${encodeURIComponent(cat.name)}" class="related-cat-card">
            <div class="related-cat-icon" style="background:${getCategoryGradient(cat.name)}">
                <i class="${getProductIcon(cat.name)}"></i>
            </div>
            <div class="related-cat-info">
                <h4>${cat.name}</h4>
                <span>${countText}</span>
            </div>
            <i class="fas fa-arrow-right related-cat-arrow"></i>
        </a>
    `}).join('');
}

// ========================================
// FILTER BUTTONS
// ========================================
function renderFilterButtons(container, categories) {
    const allBtn = container.querySelector('.filter-btn');
    container.innerHTML = '';
    container.appendChild(allBtn);

    categories.forEach(cat => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn';
        btn.onclick = function() {
            filterProducts(cat.name, this);
            // Update URL without reload
            const url = new URL(window.location);
            url.searchParams.set('category', cat.name);
            window.history.pushState({}, '', url);
            showCategoryHero(cat.name);
            showRelatedCategories(cat.name);
        };

        const icon = getProductIcon(cat.name);
        btn.innerHTML = `<i class="${icon}" style="margin-right:0.35rem;font-size:0.8em"></i>${cat.name}<span class="filter-count" data-category="${cat.name}"></span>`;
        container.appendChild(btn);
    });

    // "Tất cả" button should reset to default view
    allBtn.onclick = function() {
        filterProducts('all', this);
        const url = new URL(window.location);
        url.searchParams.delete('category');
        window.history.pushState({}, '', url);
        // Show default header, hide category hero + related
        const defaultHeader = document.getElementById('defaultPageHeader');
        const heroSection = document.getElementById('categoryHero');
        const relatedSection = document.getElementById('relatedCategories');
        if (defaultHeader) defaultHeader.style.display = '';
        if (heroSection) heroSection.style.display = 'none';
        if (relatedSection) relatedSection.style.display = 'none';
    };
}

// Update category counts
function updateCategoryCounts() {
    const countEls = document.querySelectorAll('.filter-count');
    countEls.forEach(el => {
        const catName = el.dataset.category;
        const count = allProducts.filter(p =>
            (p.category_id?.name || '').toLowerCase() === catName.toLowerCase()
        ).length;
        el.textContent = count > 0 ? ` (${count})` : '';
    });
}

// ========================================
// PRODUCTS GRID
// ========================================
function renderProductsGrid(products) {
    const container = document.getElementById('productsGrid');
    if (!container) return;

    if (products.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-search" style="color:var(--gray-400)"></i>
                <p>Không tìm thấy dự án nào trong danh mục này</p>
                <a href="products.html" class="btn btn-primary" style="margin-top:1rem">Xem tất cả dự án</a>
            </div>
        `;
        return;
    }

    container.innerHTML = products.map(product => {
        return `
        <div class="product-card" data-id="${product.id}" data-category="${product.category_id?.name || ''}" onclick="viewProduct(${product.id})" style="cursor:pointer">
            <div class="product-image">
                <img src="${getProductImage(product.category_id?.name)}" alt="${product.name}" class="product-img">
                ${product.stock_quantity < 5 ? '<span class="product-badge">Hot</span>' : ''}
            </div>
            <div class="product-content">
                <span class="product-category">${product.category_id?.name || 'Dự án CNTT'}</span>
                <h3 class="product-title">${product.name}</h3>
                <p class="product-description">${product.description || 'Giải pháp công nghệ thông tin chất lượng cao.'}</p>
                <div class="product-footer">
                    <div class="product-price">
                        ${formatCurrency(product.price)}
                    </div>
                    <div style="display:flex;gap:0.5rem">
                        <button class="add-to-cart-btn" title="Xem chi tiết" onclick="event.stopPropagation(); viewProduct(${product.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="add-to-cart-btn" title="Thêm vào giỏ" onclick="event.stopPropagation(); addToCartById(${product.id})" style="background:var(--primary-500);color:white">
                            <i class="fas fa-cart-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `}).join('');
}

// Add to cart by product ID
function addToCartById(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (product) {
        addToCart(product);
    }
}

// Filter Products
function filterProducts(category, buttonElement) {
    currentFilter = category;

    if (buttonElement) {
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        buttonElement.classList.add('active');
    }

    let filteredProducts;
    if (category === 'all') {
        filteredProducts = allProducts;
    } else {
        filteredProducts = allProducts.filter(p =>
            p.category_id?.name?.toLowerCase().includes(category.toLowerCase())
        );
    }

    renderProductsGrid(filteredProducts);
}

// Search Products
function searchProducts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();

    let filteredProducts = allProducts.filter(product => {
        const matchesSearch =
            product.name.toLowerCase().includes(searchTerm) ||
            (product.description || '').toLowerCase().includes(searchTerm) ||
            (product.category_id?.name || '').toLowerCase().includes(searchTerm);

        const matchesFilter = currentFilter === 'all' ||
            (product.category_id?.name || '').toLowerCase().includes(currentFilter.toLowerCase());

        return matchesSearch && matchesFilter;
    });

    renderProductsGrid(filteredProducts);
}

// ========================================
// PRODUCT ICONS & IMAGES
// ========================================
function getProductIcon(category) {
    const icons = {
        'Website': 'fas fa-globe',
        'E-Commerce': 'fas fa-shopping-cart',
        'Mobile App': 'fas fa-mobile-alt',
        'ERP': 'fas fa-building',
        'CRM': 'fas fa-users',
        'Booking': 'fas fa-calendar-check',
        'API': 'fas fa-plug',
        'Database': 'fas fa-database',
        'AI/ML': 'fas fa-brain',
        'Cloud': 'fas fa-cloud'
    };
    return icons[category] || 'fas fa-project-diagram';
}

function getProductImage(category) {
    const images = {
        'Website': 'images/products/website.png',
        'E-Commerce': 'images/products/ecommerce.png',
        'Mobile App': 'images/products/mobile-app.png',
        'ERP': 'images/products/erp.png',
        'CRM': 'images/products/crm.png'
    };
    return images[category] || 'images/products/website.png';
}

// ========================================
// PRODUCT DETAIL MODAL
// ========================================
function viewProduct(productId) {
    const product = allProducts.find(p => p.id === productId);
    if (!product) return;

    const category = product.category_id?.name || 'Dự án CNTT';
    let stockText;
    if (product.stock_quantity > 5) {
        stockText = '<span style="color:#22c55e"><i class="fas fa-check-circle"></i> Còn hàng (' + product.stock_quantity + ')</span>';
    } else if (product.stock_quantity > 0) {
        stockText = '<span style="color:#f59e0b"><i class="fas fa-exclamation-circle"></i> Sắp hết (' + product.stock_quantity + ')</span>';
    } else {
        stockText = '<span style="color:#ef4444"><i class="fas fa-times-circle"></i> Hết hàng</span>';
    }

    const modalHTML = `
        <div class="modal-overlay active" id="productDetailModal" onclick="if(event.target===this)closeProductModal()">
            <div class="modal modal-lg" style="max-width:700px">
                <button class="modal-close" onclick="closeProductModal()">
                    <i class="fas fa-times"></i>
                </button>
                <div style="padding:0">
                    <div style="position:relative;height:220px;overflow:hidden;border-radius:var(--radius-lg) var(--radius-lg) 0 0;background:${getCategoryGradient(category)}">
                        <img src="${getProductImage(category)}" alt="${product.name}"
                            style="width:100%;height:100%;object-fit:cover;opacity:0.3">
                        <div style="position:absolute;bottom:1.5rem;left:1.5rem;right:1.5rem;color:white">
                            <span style="background:rgba(255,255,255,0.2);padding:0.25rem 0.75rem;border-radius:20px;font-size:0.8rem">
                                <i class="${getProductIcon(category)}"></i> ${category}
                            </span>
                            <h2 style="margin-top:0.5rem;font-size:1.5rem">${product.name}</h2>
                        </div>
                    </div>
                    <div style="padding:1.5rem">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:0.5rem">
                            <div style="font-size:1.5rem;font-weight:700;color:var(--primary-600)">${formatCurrency(product.price)}</div>
                            <div>${stockText}</div>
                        </div>
                        <h4 style="color:var(--gray-800);margin-bottom:0.5rem"><i class="fas fa-info-circle" style="color:var(--primary-500)"></i> Mô tả chi tiết</h4>
                        <p style="color:var(--gray-600);line-height:1.8;margin-bottom:1.5rem">${product.description || 'Giải pháp công nghệ thông tin chất lượng cao, được phát triển bởi đội ngũ Phong Asia.'}</p>
                        <div style="display:flex;gap:1rem;flex-wrap:wrap">
                            <button class="btn btn-primary btn-lg" style="flex:1" onclick="addToCartById(${product.id}); closeProductModal(); showToast('Đã thêm vào giỏ hàng!', 'success')">
                                <i class="fas fa-cart-plus"></i> Thêm Vào Giỏ Hàng
                            </button>
                            <button class="btn btn-lg" style="flex:1;border:1px solid var(--gray-300);background:white" onclick="closeProductModal()">
                                <i class="fas fa-arrow-left"></i> Quay Lại
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    const existing = document.getElementById('productDetailModal');
    if (existing) existing.remove();

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.body.style.overflow = 'hidden';
}

function closeProductModal() {
    const modal = document.getElementById('productDetailModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeProductModal();
});

// ========================================
// DEMO PRODUCTS (fallback)
// ========================================
function getDemoProducts() {
    return [
        {
            id: 1,
            name: 'Hệ Thống Quản Lý Bán Hàng POS',
            description: 'Giải pháp quản lý bán hàng toàn diện với tính năng thanh toán, quản lý kho, báo cáo doanh thu. Hỗ trợ đa chi nhánh và đồng bộ dữ liệu thời gian thực.',
            price: 15000000,
            category_id: { name: 'Website' },
            stock_quantity: 10
        },
        {
            id: 2,
            name: 'Website Thương Mại Điện Tử',
            description: 'Website bán hàng trực tuyến với giỏ hàng, thanh toán online, quản lý đơn hàng. Tích hợp các cổng thanh toán phổ biến.',
            price: 25000000,
            category_id: { name: 'E-Commerce' },
            stock_quantity: 5
        },
        {
            id: 3,
            name: 'Ứng Dụng Mobile iOS/Android',
            description: 'Ứng dụng di động đa nền tảng iOS/Android với UI/UX hiện đại. Sử dụng React Native hoặc Flutter.',
            price: 35000000,
            category_id: { name: 'Mobile App' },
            stock_quantity: 3
        },
        {
            id: 4,
            name: 'Hệ Thống ERP Doanh Nghiệp',
            description: 'Giải pháp quản lý tổng thể doanh nghiệp: nhân sự, kế toán, kho, sản xuất. Tùy chỉnh theo quy mô doanh nghiệp.',
            price: 50000000,
            category_id: { name: 'ERP' },
            stock_quantity: 2
        },
        {
            id: 5,
            name: 'CRM Quản Lý Khách Hàng',
            description: 'Phần mềm quản lý quan hệ khách hàng, tự động hóa bán hàng và marketing. Tích hợp email, SMS marketing.',
            price: 20000000,
            category_id: { name: 'CRM' },
            stock_quantity: 8
        },
        {
            id: 6,
            name: 'Hệ Thống Đặt Lịch Hẹn Online',
            description: 'Giải pháp đặt lịch online cho spa, salon, phòng khám, dịch vụ. Tự động nhắc nhở và quản lý lịch.',
            price: 12000000,
            category_id: { name: 'Website' },
            stock_quantity: 15
        },
        {
            id: 7,
            name: 'Website Giới Thiệu Doanh Nghiệp',
            description: 'Website corporate chuyên nghiệp với thiết kế hiện đại, responsive, SEO friendly.',
            price: 8000000,
            category_id: { name: 'Website' },
            stock_quantity: 20
        },
        {
            id: 8,
            name: 'Hệ Thống Quản Lý Nhà Hàng',
            description: 'Phần mềm quản lý nhà hàng, quán cafe với order, bếp, thu ngân, báo cáo. Hỗ trợ QR menu.',
            price: 18000000,
            category_id: { name: 'ERP' },
            stock_quantity: 7
        },
        {
            id: 9,
            name: 'App Giao Hàng & Logistics',
            description: 'Ứng dụng quản lý giao hàng với tracking realtime, tối ưu lộ trình, báo cáo hiệu suất.',
            price: 40000000,
            category_id: { name: 'Mobile App' },
            stock_quantity: 4
        },
        {
            id: 10,
            name: 'Platform Học Trực Tuyến LMS',
            description: 'Hệ thống quản lý học tập với video, bài kiểm tra, chứng chỉ, thanh toán khóa học.',
            price: 45000000,
            category_id: { name: 'E-Commerce' },
            stock_quantity: 3
        },
        {
            id: 11,
            name: 'Hệ Thống Quản Lý Kho WMS',
            description: 'Phần mềm quản lý kho hàng với barcode, RFID, xuất nhập kho, kiểm kê tự động.',
            price: 30000000,
            category_id: { name: 'ERP' },
            stock_quantity: 5
        },
        {
            id: 12,
            name: 'App Đặt Xe & Di Chuyển',
            description: 'Ứng dụng đặt xe như Grab với matching driver, thanh toán, đánh giá, theo dõi trip.',
            price: 55000000,
            category_id: { name: 'Mobile App' },
            stock_quantity: 2
        }
    ];
}
