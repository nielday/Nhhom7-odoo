# Customer Management Web Frontend

Frontend application cho hệ thống Customer Management với tích hợp Proxy Server.

## Tính năng

- 🔐 Xác thực JWT
- 🛒 Giỏ hàng và đặt hàng
- 👤 Quản lý tài khoản
- 📦 Danh sách sản phẩm
- 🔄 Proxy server tích hợp (giải quyết CORS)

## Cấu trúc thư mục

```
customer-management-web/
├── index.html          # Trang chủ
├── products.html       # Trang sản phẩm
├── account.html        # Trang quản lý tài khoản
├── about.html          # Giới thiệu
├── contact.html        # Liên hệ
├── proxy-server.js     # Proxy server (Node.js)
├── package.json        # Node.js dependencies
├── start.sh           # Script khởi động
├── css/
│   └── style.css      # Styles
└── js/
    ├── api.js         # API client
    ├── auth.js        # Authentication
    ├── cart.js        # Shopping cart
    ├── config.js      # Configuration
    ├── main.js        # Main application
    ├── account.js     # Account management
    └── products.js    # Products page
```

## Yêu cầu

- Node.js (đã cài: `node --version`)
- npm (đã cài: `npm --version`)
- Odoo server chạy trên port 8069

## Cài đặt

1. Cài đặt dependencies:
```bash
cd /home/rynxu/Odoo-Project/customer-management-web
npm install
```

## Chạy ứng dụng

### Cách 1: Sử dụng script khởi động

```bash
./start.sh
```

### Cách 2: Chạy trực tiếp

```bash
npm start
```

Hoặc:

```bash
node proxy-server.js
```

## Truy cập

- **Frontend**: http://localhost:3000
- **Backend API** (qua proxy): http://localhost:3000/api/*
- **Odoo Backend** (trực tiếp): http://localhost:8069

## Proxy Server

Proxy server được tạo để:
- ✅ Giải quyết vấn đề CORS
- ✅ Serve static files (HTML, CSS, JS)
- ✅ Proxy API requests đến Odoo backend
- ✅ Tự động thêm CORS headers

### Cách hoạt động

```
Browser → http://localhost:3000/
  ↓
Proxy Server (Node.js)
  ├─→ Static files (HTML/CSS/JS) → Browser
  └─→ /api/* requests → Odoo (http://localhost:8069) → Browser
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký tài khoản
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/me` - Lấy thông tin tài khoản
- `POST /api/auth/update-profile` - Cập nhật thông tin
- `POST /api/auth/change-password` - Đổi mật khẩu
- `POST /api/auth/my-orders` - Lấy danh sách đơn hàng
- `POST /api/auth/verify` - Xác thực token

### Products
- `GET /api/products` - Danh sách sản phẩm
- `GET /api/products/{id}` - Chi tiết sản phẩm

### Orders
- `POST /api/orders` - Tạo đơn hàng

### Categories
- `GET /api/product-categories` - Danh sách danh mục

## Cấu hình

Chỉnh sửa trong `js/config.js`:

```javascript
const CONFIG = {
    API_BASE_URL: '',  // Empty = same origin (proxy)
    // ...
};
```

## Tắt server

Nhấn `Ctrl+C` trong terminal

## Troubleshooting

### Port 3000 đã được sử dụng

Chỉnh sửa `proxy-server.js`:
```javascript
const PORT = 3000; // Đổi thành port khác, ví dụ: 3001
```

### Odoo không chạy

Đảm bảo Odoo server đang chạy:
```bash
cd /home/rynxu/Odoo-Project
make run
```

### Lỗi CORS

Proxy server đã xử lý CORS tự động. Nếu vẫn gặp lỗi:
1. Xóa cache browser
2. Restart proxy server
3. Kiểm tra Odoo server đang chạy

## Development

Để phát triển, chỉnh sửa các file trong `js/` và `css/`, sau đó refresh browser.

## Production

Để deploy production, có thể sử dụng:
- PM2 để quản lý Node.js process
- Nginx làm reverse proxy
- SSL certificate (Let's Encrypt)

## License

MIT
