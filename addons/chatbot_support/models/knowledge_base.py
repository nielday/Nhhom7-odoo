# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ChatbotKnowledgeBase(models.Model):
    _name = 'chatbot.knowledge.base'
    _description = 'Knowledge Base cho Chatbot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(string='Tiêu đề', required=True, tracking=True)
    content = fields.Html(string='Nội dung', tracking=True, help='Nội dung sẽ được tự động điền khi import PDF')
    content_plain = fields.Text(string='Nội dung (Plain Text)', compute='_compute_content_plain', store=True)
    
    category = fields.Selection([
        ('faq', 'FAQ - Câu hỏi thường gặp'),
        ('product', 'Thông tin sản phẩm'),
        ('policy', 'Chính sách & Quy định'),
        ('guide', 'Hướng dẫn sử dụng'),
        ('other', 'Khác')
    ], string='Danh mục', default='faq', required=True, tracking=True)
    
    keywords = fields.Char(string='Từ khóa', help='Các từ khóa cách nhau bởi dấu phẩy')
    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Trung bình'),
        ('2', 'Cao'),
        ('3', 'Rất cao')
    ], string='Độ ưu tiên', default='1')
    
    active = fields.Boolean(string='Kích hoạt', default=True)
    
    # Vector embedding (lưu dưới dạng JSON string)
    embedding_vector = fields.Text(string='Vector Embedding', readonly=True)
    embedding_model = fields.Char(string='Embedding Model', readonly=True, default='none')
    
    # Metadata
    source_type = fields.Selection([
        ('manual', 'Nhập thủ công'),
        ('product', 'Từ sản phẩm'),
        ('order', 'Từ đơn hàng'),
        ('import', 'Import file')
    ], string='Nguồn', default='manual')
    
    product_id = fields.Many2one('khach_hang.product', string='Sản phẩm liên quan', ondelete='cascade')
    
    # PDF Import
    pdf_file = fields.Binary(string='File PDF', attachment=True, help='Upload file PDF để tự động trích xuất nội dung')
    pdf_filename = fields.Char(string='Tên file PDF')
    
    usage_count = fields.Integer(string='Số lần sử dụng', default=0, readonly=True)
    last_used = fields.Datetime(string='Lần dùng cuối', readonly=True)
    
    @api.depends('content')
    def _compute_content_plain(self):
        """Convert HTML content to plain text for embedding"""
        from html.parser import HTMLParser
        
        class MLStripper(HTMLParser):
            def __init__(self):
                super().__init__()
                self.reset()
                self.strict = False
                self.convert_charrefs = True
                self.text = []
            
            def handle_data(self, d):
                self.text.append(d)
            
            def get_data(self):
                return ''.join(self.text)
        
        for record in self:
            if record.content:
                s = MLStripper()
                s.feed(record.content)
                record.content_plain = s.get_data()
            else:
                record.content_plain = ''
    
    @api.model
    def create(self, vals):
        """Override create to generate embedding"""
        record = super(ChatbotKnowledgeBase, self).create(vals)
        # TODO: Trigger embedding generation in background
        return record
    
    def write(self, vals):
        """Override write to regenerate embedding if content changes"""
        result = super(ChatbotKnowledgeBase, self).write(vals)
        if 'content' in vals or 'content_plain' in vals:
            # TODO: Trigger embedding regeneration
            pass
        return result
    
    def action_generate_embedding(self):
        """Manual action to generate/regenerate embedding"""
        # TODO: Call RAG service to generate embedding
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': 'Đã tạo embedding cho tài liệu này',
                'type': 'success',
            }
        }
    
    def increment_usage(self):
        """Increment usage counter when document is used in RAG"""
        self.ensure_one()
        self.sudo().write({
            'usage_count': self.usage_count + 1,
            'last_used': fields.Datetime.now()
        })
    
    def action_import_pdf(self):
        """Import PDF file and extract text content with chunking"""
        self.ensure_one()
        
        if not self.pdf_file:
            raise ValidationError("Vui lòng upload file PDF trước!")
        
        try:
            import base64
            import io
            import re
            
            # Try PyPDF2 first
            try:
                from PyPDF2 import PdfReader
                
                # Decode base64 PDF file
                pdf_data = base64.b64decode(self.pdf_file)
                pdf_file = io.BytesIO(pdf_data)
                
                # Extract text from PDF
                reader = PdfReader(pdf_file)
                text_content = []
                
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
                
                full_text = "\n\n".join(text_content)
                
            except ImportError:
                raise ValidationError(
                    "Cần cài đặt thư viện PyPDF2!\n"
                    "Chạy: pip install PyPDF2"
                )
            
            if not full_text.strip():
                raise ValidationError("Không thể trích xuất text từ PDF. File có thể là ảnh scan.")
            
            # Smart chunking: Split by paragraphs and combine into ~500 word chunks
            paragraphs = re.split(r'\n\n+', full_text)
            chunks = []
            current_chunk = []
            current_length = 0
            max_chunk_words = 500
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                    
                words = len(para.split())
                
                if current_length + words > max_chunk_words and current_chunk:
                    # Save current chunk
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                    current_length = words
                else:
                    current_chunk.append(para)
                    current_length += words
            
            # Don't forget last chunk
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            
            # If only one chunk, just update this record
            if len(chunks) == 1:
                self.write({
                    'content': f'<pre>{chunks[0]}</pre>',
                    'source_type': 'import'
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Thành công!',
                        'message': f'Đã import {len(reader.pages)} trang từ PDF: {self.pdf_filename}',
                        'type': 'success',
                    }
                }
            
            # Multiple chunks - create separate KB entries for each
            base_name = self.name or self.pdf_filename.replace('.pdf', '')
            
            # Update first record with first chunk
            self.write({
                'name': f'{base_name} (Phần 1/{len(chunks)})',
                'content': f'<pre>{chunks[0]}</pre>',
                'source_type': 'import'
            })
            
            # Create new records for remaining chunks
            for i, chunk in enumerate(chunks[1:], 2):
                self.create({
                    'name': f'{base_name} (Phần {i}/{len(chunks)})',
                    'content': f'<pre>{chunk}</pre>',
                    'category': self.category,
                    'priority': self.priority,
                    'keywords': self.keywords,
                    'source_type': 'import',
                    'pdf_filename': self.pdf_filename,
                })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành công!',
                    'message': f'Đã import {len(reader.pages)} trang và tạo {len(chunks)} chunks từ PDF: {self.pdf_filename}',
                    'type': 'success',
                }
            }
            
        except Exception as e:
            raise ValidationError(f"Lỗi khi import PDF: {str(e)}")
