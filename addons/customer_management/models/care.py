# models/care.py
from odoo import models, fields

class CareActivity(models.Model):
    _name = 'khach_hang.care_activity'
    _description = 'Hoạt Động Chăm Sóc'
    _order = 'care_date desc'  # Sắp xếp theo ngày chăm sóc mới nhất

    customer_id = fields.Many2one('khach_hang.customer', string='Khách Hàng', required=True)
    care_date = fields.Date(string='Ngày Chăm Sóc', required=True)
    care_staff = fields.Many2one('res.users', string='Nhân Viên Chăm Sóc', default=lambda self: self.env.user)
    contact_method = fields.Selection([
        ('phone', 'Điện Thoại'),
        ('email', 'Email'),
        ('direct', 'Gặp Trực Tiếp'),
    ], string='Hình Thức Liên Hệ', required=True)
    notes = fields.Text(string='Ghi Chú')