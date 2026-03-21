# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class OrderTaskIntegration(models.Model):
    """Mở rộng model Order để tự động tạo Task khi tạo đơn hàng"""
    _inherit = 'khach_hang.order'

    # Liên kết với Task Management
    task_ids = fields.One2many('task.management.task', 'order_id', string='Công việc liên quan')

    # Mapping trạng thái đơn hàng -> trạng thái task
    ORDER_TO_TASK_STATE = {
        'draft': {'state': 'todo', 'progress': 0},
        'confirmed': {'state': 'todo', 'progress': 20},
        'shipping': {'state': 'in_progress', 'progress': 70},
        'done': {'state': 'done', 'progress': 100},
        'cancel': {'state': 'cancel', 'progress': 0},
    }

    def _update_related_tasks(self, order_state):
        """Cập nhật trạng thái các task liên quan theo trạng thái đơn hàng"""
        task_vals = self.ORDER_TO_TASK_STATE.get(order_state, {})
        if task_vals and self.task_ids:
            self.task_ids.write(task_vals)

    @api.model
    def create(self, vals):
        """Tự động tạo Task khi tạo đơn hàng mới"""
        _logger.info("========== ORDER CREATE START ==========")
        _logger.info(f"Creating order with vals: {vals}")
        
        order = super(OrderTaskIntegration, self).create(vals)
        _logger.info(f"Order created: ID={order.id}, Name={order.name}")
        
        # Tạo task tự động cho đơn hàng
        task_vals = {
            'name': f"Xử lý đơn hàng: {order.name}",
            'description': f"""
                <p><strong>Thông tin đơn hàng:</strong></p>
                <ul>
                    <li>Mã đơn hàng: {order.name}</li>
                    <li>Khách hàng: {order.customer_id.name if order.customer_id else 'N/A'}</li>
                    <li>Tổng tiền: {order.total_amount:,.0f} VNĐ</li>
                </ul>
                <p><strong>Công việc cần thực hiện:</strong></p>
                <ul>
                    <li>Xác nhận đơn hàng</li>
                    <li>Chuẩn bị hàng hóa</li>
                    <li>Giao hàng cho khách</li>
                </ul>
            """,
            'partner_id': order.customer_id.id if order.customer_id else False,
            'order_id': order.id,
            'deadline': order.delivery_date,
            'priority': '2',  # Độ ưu tiên cao
            'state': 'todo',
            'progress': 0,
        }
        _logger.info(f"Creating task with vals: {task_vals}")
        
        task = self.env['task.management.task'].create(task_vals)
        _logger.info(f"Task created: ID={task.id}, Name={task.name}")
        _logger.info("========== ORDER CREATE END ==========")
        
        return order

    def action_confirm(self):
        """Override: Xác nhận đơn hàng và cập nhật task sang In Progress"""
        result = super(OrderTaskIntegration, self).action_confirm()
        for order in self:
            order._update_related_tasks('confirmed')
        return result

    def action_ship(self):
        """Override: Giao hàng và cập nhật task (tiến độ 70%)"""
        result = super(OrderTaskIntegration, self).action_ship()
        for order in self:
            order._update_related_tasks('shipping')
        return result

    def action_done(self):
        """Override: Hoàn thành đơn hàng và cập nhật task sang Done"""
        result = super(OrderTaskIntegration, self).action_done()
        for order in self:
            order._update_related_tasks('done')
        return result

    def action_cancel(self):
        """Override: Hủy đơn hàng và cập nhật task sang Cancel"""
        result = super(OrderTaskIntegration, self).action_cancel()
        for order in self:
            order._update_related_tasks('cancel')
        return result
