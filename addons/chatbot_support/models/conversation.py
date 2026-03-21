# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ChatbotConversation(models.Model):
    _name = 'chatbot.conversation'
    _description = 'Lịch sử hội thoại Chatbot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Tên cuộc hội thoại', compute='_compute_name', store=True)
    
    # User info
    partner_id = fields.Many2one('khach_hang.customer', string='Khách hàng', ondelete='cascade')
    session_id = fields.Char(string='Session ID', required=True, index=True)
    user_ip = fields.Char(string='IP Address')
    user_agent = fields.Char(string='User Agent')
    
    # Conversation metadata
    message_ids = fields.One2many('chatbot.message', 'conversation_id', string='Tin nhắn')
    message_count = fields.Integer(string='Số tin nhắn', compute='_compute_message_count', store=True)
    
    state = fields.Selection([
        ('active', 'Đang hoạt động'),
        ('closed', 'Đã đóng'),
        ('archived', 'Đã lưu trữ')
    ], string='Trạng thái', default='active', tracking=True)
    
    start_time = fields.Datetime(string='Bắt đầu', default=fields.Datetime.now, required=True)
    end_time = fields.Datetime(string='Kết thúc')
    duration = fields.Integer(string='Thời lượng (phút)', compute='_compute_duration', store=True)
    
    # Ratings
    rating = fields.Selection([
        ('1', '⭐ Rất tệ'),
        ('2', '⭐⭐ Tệ'),
        ('3', '⭐⭐⭐ Trung bình'),
        ('4', '⭐⭐⭐⭐ Tốt'),
        ('5', '⭐⭐⭐⭐⭐ Xuất sắc')
    ], string='Đánh giá')
    feedback = fields.Text(string='Phản hồi từ khách hàng')
    
    @api.depends('partner_id', 'create_date')
    def _compute_name(self):
        for record in self:
            if record.partner_id:
                record.name = f"Chat với {record.partner_id.name} - {record.create_date.strftime('%d/%m/%Y %H:%M')}"
            else:
                record.name = f"Chat khách vãng lai - {record.create_date.strftime('%d/%m/%Y %H:%M')}"
    
    @api.depends('message_ids')
    def _compute_message_count(self):
        for record in self:
            record.message_count = len(record.message_ids)
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = int(delta.total_seconds() / 60)
            else:
                record.duration = 0
    
    def action_close_conversation(self):
        """Close the conversation"""
        self.ensure_one()
        self.write({
            'state': 'closed',
            'end_time': fields.Datetime.now()
        })


class ChatbotMessage(models.Model):
    _name = 'chatbot.message'
    _description = 'Tin nhắn Chatbot'
    _order = 'create_date asc'

    conversation_id = fields.Many2one('chatbot.conversation', string='Cuộc hội thoại', required=True, ondelete='cascade')
    
    message_type = fields.Selection([
        ('user', 'Từ người dùng'),
        ('bot', 'Từ chatbot'),
        ('system', 'Hệ thống')
    ], string='Loại tin nhắn', required=True)
    
    content = fields.Text(string='Nội dung', required=True)
    
    # RAG metadata (for bot messages)
    retrieved_docs = fields.Text(string='Tài liệu truy xuất (JSON)', help='IDs của knowledge base documents được sử dụng')
    confidence_score = fields.Float(string='Độ tin cậy', help='Confidence score của câu trả lời')
    
    # Gemini API metadata
    model_used = fields.Char(string='Model sử dụng', default='gemini-1.5-flash')
    tokens_used = fields.Integer(string='Tokens sử dụng')
    response_time = fields.Float(string='Thời gian phản hồi (s)')
    
    # User feedback on specific message
    is_helpful = fields.Boolean(string='Hữu ích?')
    
    create_date = fields.Datetime(string='Thời gian', default=fields.Datetime.now, required=True)
