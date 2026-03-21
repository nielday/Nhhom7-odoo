# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class TaskManagement(models.Model):
    _name = 'task.management.task'
    _description = 'Quản lý Công Việc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, deadline asc'

    name = fields.Char(string='Tên công việc', required=True, tracking=True)
    description = fields.Html(string='Mô tả chi tiết') 

    partner_id = fields.Many2one('khach_hang.customer', string='Khách hàng', tracking=True)
    order_id = fields.Many2one('khach_hang.order', string='Đơn hàng liên quan', tracking=True, ondelete='cascade')
 
    nhan_vien_id = fields.Many2one('nhan_vien', string='Người thực hiện', tracking=True)
    
    start_date = fields.Date(string='Ngày bắt đầu', default=fields.Date.context_today)
    deadline = fields.Date(string='Hạn chót', tracking=True)
    
    progress = fields.Integer(string='Tiến độ (%)', default=0)
    
    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Trung bình'),
        ('2', 'Cao'),
        ('3', 'Rất quan trọng')
    ], string='Độ ưu tiên', default='1')

    state = fields.Selection([
        ('todo', 'Cần làm'),
        ('in_progress', 'Đang thực hiện'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Hủy bỏ')
    ], string='Trạng thái', default='todo', tracking=True, group_expand='_expand_states')

    @api.constrains('start_date', 'deadline')
    def _check_dates(self):
        for record in self:
            if record.deadline and record.start_date and record.deadline < record.start_date:
                raise ValidationError("Lỗi Logic: Hạn chót phải sau ngày bắt đầu!")

    @api.onchange('state')
    def _onchange_state(self):
        state_progress = {
            'todo': 0,          
            'in_progress': 50,   
            'done': 100,         
            'cancel': 0          
        }
        if self.state in state_progress:
            self.progress = state_progress[self.state]

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def action_todo(self):
        self.state = 'todo'
        self.progress = 0

    def action_in_progress(self):
        self.state = 'in_progress'
        self.progress = 50

    def action_done(self):
        self.state = 'done'
        self.progress = 100

    def action_cancel(self):
        self.state = 'cancel'
        self.progress = 0