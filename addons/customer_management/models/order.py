from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class Order(models.Model):
    _name = 'khach_hang.order'
    _description = 'Đơn Hàng'

    name = fields.Char(string='Mã Đơn Hàng', required=True)
    customer_id = fields.Many2one('khach_hang.customer', string='Khách Hàng', required=True)
    product_ids = fields.Many2many('khach_hang.product', string='Sản Phẩm')
    total_amount = fields.Float(string='Tổng Tiền', compute='_compute_total_amount')
    date_order = fields.Datetime(string='Ngày Đặt Hàng', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Xác Nhận'),
        ('shipping', 'Đang Giao'),
        ('done', 'Hoàn Thành'),
        ('cancel', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft')
    delivery_date = fields.Date(string='Ngày Giao Hàng Dự Kiến')
    delivery_days = fields.Integer(string='Số Ngày Giao Hàng', compute='_compute_delivery_days')

    @api.depends('product_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(product.price for product in record.product_ids)

    @api.depends('date_order', 'delivery_date')
    def _compute_delivery_days(self):
        for record in self:
            if record.date_order and record.delivery_date:
                order_date = fields.Date.from_string(record.date_order.date())
                delivery_date = fields.Date.from_string(record.delivery_date)
                record.delivery_days = (delivery_date - order_date).days
            else:
                record.delivery_days = 0

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_ship(self):
        self.write({'state': 'shipping'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
