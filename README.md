<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
    CÔNG NGHỆ HAY - PLATFORM ERP
</h2>
<div align="center">
    <p align="center">
        <img src="docs/logo/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="docs/logo/fitdnu_logo.png" alt="FIT Logo" width="180"/>
        <img src="docs/logo/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

## 📖 1. Giới thiệu

**Công Nghệ Hay** là nền tảng ERP được phát triển dựa trên mã nguồn mở Odoo, tập trung vào việc quản lý khách hàng, hỗ trợ tự động bằng AI Chatbot, và quản lý công việc dự án. Platform được áp dụng trong học phần **Thực tập doanh nghiệp** tại Khoa Công Nghệ Thông Tin - Đại học Đại Nam.

### 🎯 Mục tiêu dự án
- Xây dựng hệ thống quản lý khách hàng toàn diện (CRM)
- Tích hợp AI Chatbot thông minh với RAG (Retrieval-Augmented Generation)
- Quản lý công việc và tiến độ dự án hiệu quả
- Cung cấp giao diện web hiện đại cho khách hàng

## 🏗️ 2. Kiến trúc hệ thống

### 2.1. Ba module chính

#### 📊 **Customer Management** (Quản lý khách hàng)
Module CRM cốt lõi của hệ thống, quản lý toàn bộ quy trình bán hàng và chăm sóc khách hàng.

**Tính năng:**
- ✅ Quản lý thông tin khách hàng (Customer)
- ✅ Quản lý khách hàng tiềm năng (Potential Customer)
- ✅ Quản lý danh mục sản phẩm (Product Category)
- ✅ Quản lý sản phẩm/dự án CNTT (Product)
- ✅ Quản lý đơn hàng (Order)
- ✅ Quản lý phản hồi khách hàng (Feedback)
- ✅ Chăm sóc khách hàng (Customer Care)
- ✅ API endpoints cho web frontend

**Models chính:**
- `customer_management.customer` - Thông tin khách hàng
- `customer_management.product` - Sản phẩm/Dự án
- `customer_management.order` - Đơn hàng
- `customer_management.feedback` - Phản hồi

#### 🤖 **Chatbot Support** (Hỗ trợ AI Chatbot)
Module chatbot thông minh sử dụng Groq API và RAG để tư vấn khách hàng tự động.

**Tính năng:**
- ✅ Tích hợp Groq API cho câu trả lời tự nhiên
- ✅ RAG (Retrieval-Augmented Generation) truy xuất thông tin chính xác
- ✅ Quản lý Knowledge Base (FAQ, Product Info)
- ✅ Lưu trữ lịch sử hội thoại (Conversation History)
- ✅ Cấu hình chatbot (Chatbot Config)
- ✅ API endpoints cho web chat widget
- ✅ Tự động trả lời câu hỏi về sản phẩm, giá cả, đơn hàng

**Models chính:**
- `chatbot_support.knowledge_base` - Cơ sở tri thức
- `chatbot_support.conversation` - Lịch sử hội thoại
- `chatbot_support.chatbot_config` - Cấu hình chatbot

**Công nghệ AI:**
- Groq API
- RAG với vector embeddings
- Semantic search

#### 📋 **Task Management** (Quản lý công việc)
Module quản lý công việc và tiến độ dự án, tích hợp với Customer Management.

**Tính năng:**
- ✅ Quản lý danh sách công việc (Tasks)
- ✅ Theo dõi hạn chót (Deadline) & KPI
- ✅ Báo cáo tiến độ
- ✅ Tự động tạo Task khi có đơn hàng mới
- ✅ Tích hợp với module Nhân sự

**Models chính:**
- `task_management.task` - Công việc
- Kế thừa `customer_management.order` để tạo task tự động

### 2.2. Web Frontend

**Giao diện web khách hàng** (`customer-management-web/`)
- 🌐 Website hiện đại với HTML/CSS/JavaScript
- 🎨 Thiết kế responsive, mobile-friendly
- 🛒 Trang sản phẩm với giỏ hàng
- 💬 Tích hợp chatbot widget
- 📱 Liên hệ và hỗ trợ khách hàng

**Công nghệ:**
- HTML5, CSS3, JavaScript (Vanilla)
- Font Awesome icons
- Google Fonts (Inter)
- Proxy server (Node.js) để kết nối Odoo API

## 🔧 3. Công nghệ sử dụng

<div align="center">

### Hệ điều hành
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)

### Backend Framework
[![Odoo](https://img.shields.io/badge/Odoo_16-714B67?style=for-the-badge&logo=odoo&logoColor=white)](https://www.odoo.com/)
[![Python](https://img.shields.io/badge/Python_3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

### Frontend
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://html.spec.whatwg.org/)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS/)

### AI & Machine Learning
[![Groq](https://img.shields.io/badge/Groq-f55036?style=for-the-badge&logo=groq&logoColor=white)](https://console.groq.com/)

### Database
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

### DevOps
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

## ⚙️ 4. Cài đặt

### 4.1. Yêu cầu hệ thống
- Ubuntu 22.04 LTS hoặc cao hơn
- Python 3.10
- PostgreSQL 14+
- Docker & Docker Compose
- Node.js 16+ (cho web frontend)

### 4.2. Clone project

```bash
git clone https://github.com/nielday/Nhhom7-odoo.git
cd Nhhom7-odoo
```

### 4.3. Cài đặt dependencies

#### 4.3.1. Cài đặt thư viện hệ thống
```bash
sudo apt-get update
sudo apt-get install -y \
    libxml2-dev libxslt-dev libldap2-dev libsasl2-dev \
    libssl-dev python3.10-distutils python3.10-dev \
    build-essential libffi-dev zlib1g-dev python3.10-venv libpq-dev
```

#### 4.3.2. Tạo môi trường ảo Python
```bash
python3.10 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### 4.4. Setup Database

Khởi tạo PostgreSQL database bằng Docker:
```bash
sudo docker-compose up -d
```

Database sẽ chạy trên port `5431` với:
- Username: `odoo`
- Password: `odoo`
- Database: `postgres`

### 4.5. Cấu hình Odoo

Tạo file `odoo.conf` từ template:
```bash
cp odoo.conf.template odoo.conf
```

Nội dung file `odoo.conf`:
```ini
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5431
xmlrpc_port = 8069
```

### 4.6. Cấu hình Groq API (cho Chatbot)

Tạo file `.env` trong thư mục gốc:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Lấy API key tại: https://console.groq.com/keys

### 4.7. Chạy hệ thống

#### 4.7.1. Chạy Odoo Backend
```bash
python3 odoo-bin.py -c odoo.conf -u all
```

Truy cập: http://localhost:8069

#### 4.7.2. Chạy Web Frontend
```bash
cd customer-management-web
npm install
npm start
```

Truy cập: http://localhost:3000

## 📦 5. Cài đặt modules

Sau khi đăng nhập vào Odoo (http://localhost:8069):

1. Vào **Apps** → Tìm kiếm "Quản Lý Khách Hàng"
2. Cài đặt module **Customer Management**
3. Cài đặt module **AI Chatbot Support**
4. Cài đặt module **Task Management**

## 📁 6. Cấu trúc thư mục

```
Nhhom7-odoo/
├── addons/
│   ├── customer_management/      # Module quản lý khách hàng
│   │   ├── models/               # Models (Customer, Product, Order...)
│   │   ├── views/                # XML views
│   │   ├── controllers/          # API controllers
│   │   ├── security/             # Access rights
│   │   └── data/                 # Demo data
│   │
│   ├── chatbot_support/          # Module AI Chatbot
│   │   ├── models/               # Models (Conversation, Knowledge Base...)
│   │   ├── views/                # XML views
│   │   ├── controllers/          # Chatbot API
│   │   └── data/                 # Demo knowledge base
│   │
│   └── task_management/          # Module quản lý công việc
│       ├── models/               # Models (Task...)
│       ├── views/                # Kanban, List views
│       └── data/                 # Demo tasks
│
├── customer-management-web/      # Web Frontend
│   ├── index.html                # Trang chủ
│   ├── products.html             # Trang sản phẩm
│   ├── about.html                # Giới thiệu
│   ├── contact.html              # Liên hệ
│   ├── css/                      # Stylesheets
│   ├── js/                       # JavaScript
│   ├── images/                   # Ảnh sản phẩm
│   └── proxy-server.js           # Proxy to Odoo API
│
├── odoo-bin.py                   # Odoo executable
├── odoo.conf.template            # Config template
├── docker-compose.yml            # PostgreSQL container
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 7. Tính năng nổi bật

### 7.1. Quy trình bán hàng tự động
1. Khách hàng truy cập website → Xem sản phẩm
2. Chatbot AI tư vấn tự động 24/7
3. Khách hàng đặt hàng → Tạo Order trong hệ thống
4. Tự động tạo Task cho nhân viên xử lý
5. Theo dõi tiến độ qua Kanban board
6. Chăm sóc khách hàng sau bán

### 7.2. AI Chatbot thông minh
- Trả lời câu hỏi về sản phẩm, giá cả
- Tìm kiếm sản phẩm phù hợp
- Hướng dẫn đặt hàng
- Tra cứu trạng thái đơn hàng
- Học từ Knowledge Base

### 7.3. Quản lý công việc hiệu quả
- Kanban board trực quan
- Theo dõi deadline
- Báo cáo KPI

## 📊 8. Demo Data

Hệ thống đi kèm demo data cho cả 3 module:
- 50+ khách hàng mẫu
- 12+ sản phẩm/dự án CNTT
- 30+ đơn hàng
- 100+ câu hỏi trong Knowledge Base
- 20+ công việc mẫu

## 🧪 9. Testing

### 9.1. Test Backend API
```bash
# Test Customer API
curl http://localhost:8069/api/customers

# Test Product API
curl http://localhost:8069/api/products

# Test Chatbot API
curl -X POST http://localhost:8069/api/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Cho tôi xem các dự án website"}'
```

### 9.2. Test Web Frontend
Mở trình duyệt và kiểm tra:
- ✅ Trang chủ hiển thị sản phẩm nổi bật
- ✅ Trang sản phẩm có filter và search
- ✅ Chatbot widget hoạt động
- ✅ Giỏ hàng và checkout

## 🎓 10. Tài liệu tham khảo

- [Odoo Documentation](https://www.odoo.com/documentation/16.0/)
- [Groq API](https://console.groq.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 👥 11. Đóng góp

Dự án được phát triển bởi sinh viên Khoa Công Nghệ Thông Tin - Đại học Đại Nam dưới sự hướng dẫn của AIoTLab.

### Tác giả chính
- **Đào Đức Phong** - Developer

### Giảng viên hướng dẫn
- **Nguyễn Văn Nhân** - Khoa Công Nghệ Thông Tin

## 📝 12. License

© 2024-2026 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.

---

<div align="center">
    <p>Made with ❤️ by FIT-DNU Students</p>
    <p>
        <a href="https://dainam.edu.vn">DaiNam University</a> •
        <a href="https://www.facebook.com/DNUAIoTLab">AIoTLab</a>
    </p>
</div>
