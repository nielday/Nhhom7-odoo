# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ChatbotConfig(models.Model):
    _name = 'chatbot.config'
    _description = 'Cấu hình Chatbot'
    _rec_name = 'name'

    name = fields.Char(string='Tên cấu hình', default='Chatbot Configuration', required=True)
    
    # Groq API Settings
    groq_api_key = fields.Char(string='Groq API Key', required=False, default='',
                                   help='Lấy tại https://console.groq.com/keys')
    # Sắp xếp từ rẻ → đắt (giá per 1M tokens: input/output)
    groq_model = fields.Selection([
        # === PRODUCTION MODELS (ổn định, dùng cho production) ===
        ('llama-3.1-8b-instant', '⚡ Llama 3.1 8B Instant — $0.05/$0.08 (Rẻ nhất, nhanh nhất)'),
        ('openai/gpt-oss-20b', '💰 GPT-OSS 20B — $0.075/$0.30 (Rẻ, chất lượng tốt)'),
        ('llama-3.3-70b-versatile', '⭐ Llama 3.3 70B — $0.59/$0.79 (Khuyến nghị)'),
        ('openai/gpt-oss-120b', '🏆 GPT-OSS 120B — $0.15/$0.60 (OpenAI, reasoning)'),
        # === PREVIEW MODELS (thử nghiệm, có thể thay đổi) ===
        ('qwen/qwen3-32b', '🧪 Qwen3 32B — Preview (32K context)'),
        ('meta-llama/llama-4-scout-17b-16e-instruct', '🧪 Llama 4 Scout 17B — Preview'),
        ('meta-llama/llama-4-maverick-17b-128e-instruct', '🧪 Llama 4 Maverick 17B — Preview (128 experts)'),
        ('moonshotai/kimi-k2-instruct-0905', '🧪 Kimi K2 — Preview (Moonshot AI)'),
    ], string='Model LLM', default='llama-3.3-70b-versatile', required=True,
       help='Production = ổn định, Preview = thử nghiệm. Giá tính per 1M tokens (input/output).')
    
    # RAG Settings
    top_k_results = fields.Integer(string='Top K Documents', default=3, 
                                     help='Số lượng documents truy xuất từ vector DB')
    similarity_threshold = fields.Float(string='Ngưỡng tương đồng', default=0.5,
                                         help='Chỉ lấy documents có similarity > threshold')
    
    # Chatbot Behavior
    system_prompt = fields.Text(string='System Prompt', default="""Bạn là trợ lý AI thông minh của công ty, chuyên tư vấn khách hàng.

Nhiệm vụ của bạn:
- Trả lời câu hỏi của khách hàng một cách chính xác, lịch sự và chuyên nghiệp
- Sử dụng thông tin từ knowledge base được cung cấp để trả lời
- Nếu không có thông tin trong knowledge base, hãy thừa nhận và đề xuất liên hệ nhân viên
- Luôn giữ thái độ thân thiện và hỗ trợ tối đa

Quy tắc:
- Trả lời bằng tiếng Việt
- Ngắn gọn, súc tích nhưng đầy đủ thông tin
- Không bịa đặt thông tin không có trong knowledge base
- Nếu khách hàng hỏi về giá cả, chính sách, hãy dựa vào dữ liệu chính xác""")
    
    welcome_message = fields.Text(string='Tin nhắn chào mừng', 
                                    default='Xin chào! Tôi là trợ lý AI. Tôi có thể giúp gì cho bạn? 😊')
    
    fallback_message = fields.Text(string='Tin nhắn dự phòng',
                                     default='Xin lỗi, tôi chưa có đủ thông tin để trả lời câu hỏi này. Bạn có thể liên hệ nhân viên hỗ trợ để được tư vấn chi tiết hơn.')
    
    # Performance Settings
    max_tokens = fields.Integer(string='Max Tokens', default=1000)
    temperature = fields.Float(string='Temperature', default=0.7, 
                                help='0.0 = deterministic, 1.0 = creative')
    
    # Features
    enable_conversation_history = fields.Boolean(string='Lưu lịch sử hội thoại', default=True)
    enable_rating = fields.Boolean(string='Cho phép đánh giá', default=True)
    enable_human_handoff = fields.Boolean(string='Chuyển cho nhân viên', default=True)
    
    # Active config
    active = fields.Boolean(string='Kích hoạt', default=True)
    
    @api.constrains('top_k_results')
    def _check_top_k(self):
        for record in self:
            if record.top_k_results < 1 or record.top_k_results > 10:
                raise ValidationError("Top K phải từ 1 đến 10")
    
    @api.constrains('similarity_threshold')
    def _check_threshold(self):
        for record in self:
            if record.similarity_threshold < 0 or record.similarity_threshold > 1:
                raise ValidationError("Ngưỡng tương đồng phải từ 0.0 đến 1.0")
    
    @api.constrains('temperature')
    def _check_temperature(self):
        for record in self:
            if record.temperature < 0 or record.temperature > 2:
                raise ValidationError("Temperature phải từ 0.0 đến 2.0")
    
    @api.model
    def get_active_config(self):
        """Get the active chatbot configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise ValidationError("Chưa có cấu hình chatbot nào được kích hoạt!")
        return config
