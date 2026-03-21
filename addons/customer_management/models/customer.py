from odoo import models, fields, api
from odoo.exceptions import ValidationError
import hashlib
import secrets

class Customer(models.Model):
    _name = 'khach_hang.customer'
    _description = 'Khách Hàng'

    name = fields.Char(string='Tên', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Điện Thoại')
    address = fields.Text(string='Địa Chỉ')
    
    # Authentication fields
    username = fields.Char(string='Tên đăng nhập', index=True)
    password_hash = fields.Char(string='Mật khẩu (hash)', readonly=True)
    
    order_ids = fields.One2many('khach_hang.order', 'customer_id', string='Đơn Hàng')
    feedback_ids = fields.One2many('khach_hang.feedback', 'customer_id', string='Phản Hồi')
    care_activity_ids = fields.One2many('khach_hang.care_activity', 'customer_id', string='Hoạt Động Chăm Sóc')
    order_count = fields.Integer(
        string='Số Đơn Hàng',
        compute='_compute_order_count',
        store=True
    )

    _sql_constraints = [
        ('username_unique', 'UNIQUE(username)', 'Tên đăng nhập đã tồn tại!')
    ]

    @api.depends('order_ids')
    def _compute_order_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    def _hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"

    def _verify_password(self, password):
        """Verify password against stored hash"""
        if not self.password_hash:
            return False
        try:
            salt, pwd_hash = self.password_hash.split('$')
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
        except:
            return False

    def set_password(self, password):
        """Set password for customer"""
        if len(password) < 6:
            raise ValidationError("Mật khẩu phải có ít nhất 6 ký tự!")
        self.password_hash = self._hash_password(password)