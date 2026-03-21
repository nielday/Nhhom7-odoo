from odoo import models, fields, api

class PotentialCustomer(models.Model):
    _name = 'khach_hang.potential_customer'
    _description = 'Khách Hàng Tiềm Năng'
    _order = 'contact_date desc'  # Sắp xếp theo ngày liên hệ gần nhất

    name = fields.Char(string='Tên', required=True)
    product_type = fields.Selection([
        ('electronics', 'Điện Tử'),
        ('clothing', 'Quần Áo'),
        ('food', 'Thực Phẩm'),
    ], string='Loại Mặt Hàng')
    contact_info = fields.Char(string='Thông Tin Liên Hệ')
    source = fields.Selection([
        ('advertising', 'Quảng Cáo'),
        ('referral', 'Giới Thiệu'),
        ('self_search', 'Tự Tìm Kiếm'),
    ], string='Nguồn Khách Hàng', default='self_search')
    interest_level = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung Bình'),
        ('high', 'Cao'),
    ], string='Mức Độ Quan Tâm', default='medium')
    contact_date = fields.Date(string='Ngày Liên Hệ Gần Nhất', default=fields.Date.today)
    notes = fields.Text(string='Ghi Chú')
    potential_value = fields.Float(string='Giá Trị Tiềm Năng', default=0.0)

    def action_convert_to_customer(self):
        """Chuyển đổi khách hàng tiềm năng thành khách hàng chính thức"""
        for record in self:
            customer = self.env['khach_hang.customer'].create({
                'name': record.name,
                'email': record.contact_info if '@' in record.contact_info else False,
                'phone': record.contact_info if '@' not in record.contact_info else False,
                'address': record.notes or False,  # Tạm dùng ghi chú làm địa chỉ
            })
            # Có thể thêm logic xóa hoặc đánh dấu khách hàng tiềm năng đã chuyển đổi
            record.write({'notes': f'Đã chuyển thành khách hàng {customer.id}'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Khách Hàng',
            'res_model': 'khach_hang.customer',
            'view_mode': 'form',
            'res_id': customer.id,
            'target': 'current',
        }