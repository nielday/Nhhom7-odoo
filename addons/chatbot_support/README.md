# AI Chatbot Support - RAG với Gemini API

## 📋 Tổng quan

Module chatbot thông minh tích hợp RAG (Retrieval-Augmented Generation) với Gemini AI để hỗ trợ tư vấn khách hàng tự động.

## ✨ Tính năng

- 🤖 **AI Chatbot** với Gemini 1.5 Flash
- 📚 **Knowledge Base** quản lý tài liệu, FAQ
- 🔍 **RAG Pipeline** truy xuất thông tin chính xác
- 💬 **Chat Widget** đẹp mắt, responsive
- 📊 **Lịch sử hội thoại** và analytics
- ⭐ **Đánh giá** chất lượng chatbot

## 🚀 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install requests
```

### 2. Install module trong Odoo

```bash
# Stop Odoo server nếu đang chạy (Ctrl+C)

# Update module list và install
cd /home/quoc/16-06-N01
source venv/bin/activate
python3 odoo-bin -c odoo.conf -d odoo -i chatbot_support --stop-after-init

# Restart Odoo server
python3 odoo-bin -c odoo.conf
```

### 3. Cấu hình Gemini API

1. Lấy API key tại: https://aistudio.google.com/app/apikey
2. Vào Odoo: **AI Chatbot > Cấu hình**
3. Nhập **Gemini API Key**
4. Lưu cấu hình

## 📖 Hướng dẫn sử dụng

### Quản lý Knowledge Base

1. Vào **AI Chatbot > Knowledge Base**
2. Tạo tài liệu mới:
   - **Tiêu đề**: Tên câu hỏi/chủ đề
   - **Danh mục**: FAQ, Product, Policy, Guide
   - **Nội dung**: Thông tin chi tiết
   - **Từ khóa**: Các từ khóa liên quan
3. Nhấn **Lưu**

### Tích hợp Chat Widget vào Website

Widget đã được tự động thêm vào `customer-management-web/index.html`.

Để thêm vào trang khác:

```html
<!-- Trong <head> -->
<link rel="stylesheet" href="css/chatbot.css">

<!-- Trước </body> -->
<script src="js/chatbot-widget.js"></script>
```

### Xem lịch sử chat

1. Vào **AI Chatbot > Lịch sử Chat**
2. Xem các cuộc hội thoại
3. Kiểm tra đánh giá và feedback

## 🔧 Cấu hình nâng cao

### Tùy chỉnh System Prompt

Vào **AI Chatbot > Cấu hình > Prompts & Messages** để chỉnh sửa:
- System Prompt (hành vi chatbot)
- Welcome Message (tin nhắn chào)
- Fallback Message (khi không biết câu trả lời)

### Tùy chỉnh RAG Settings

- **Top K Results**: Số lượng documents truy xuất (mặc định: 3)
- **Similarity Threshold**: Ngưỡng tương đồng (0.0 - 1.0)
- **Temperature**: Độ sáng tạo của AI (0.0 - 2.0)

## 📡 API Endpoints

### Chat API
```bash
POST /chatbot/api/chat
Content-Type: application/json

{
  "message": "Giờ làm việc của công ty?",
  "session_id": "session_123",
  "partner_id": 1
}
```

### Welcome Message
```bash
GET /chatbot/api/welcome
```

### Rate Conversation
```bash
POST /chatbot/api/rate
{
  "conversation_id": 1,
  "rating": 5,
  "feedback": "Rất hữu ích!"
}
```

## 🎨 Tùy chỉnh giao diện

Chỉnh sửa file `customer-management-web/css/chatbot.css` để thay đổi:
- Màu sắc
- Kích thước
- Vị trí widget
- Animations

## 🔍 Troubleshooting

### Chatbot không trả lời
- Kiểm tra Gemini API key đã đúng chưa
- Kiểm tra Knowledge Base có dữ liệu chưa
- Xem log Odoo để debug

### Widget không hiển thị
- Kiểm tra đã include CSS và JS chưa
- Mở Console để xem lỗi JavaScript
- Kiểm tra CORS settings

## 📝 TODO / Cải tiến

- [ ] Implement vector embeddings với ChromaDB
- [ ] Thêm multi-language support
- [ ] Tích hợp với Odoo Live Chat
- [ ] Analytics dashboard
- [ ] Export chat history

## 👨‍💻 Tác giả

**Vũ Minh Quốc** - Bài tập lớn môn Thực tập Doanh nghiệp

## 📄 License

LGPL-3
