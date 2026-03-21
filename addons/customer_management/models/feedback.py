from odoo import models, fields, api

class Feedback(models.Model):
    _name = 'khach_hang.feedback'
    _description = 'Phản Hồi'
    _inherit = ['mail.thread']

    customer_id = fields.Many2one('khach_hang.customer', string='Khách Hàng', required=True)
    question = fields.Text(string='Câu Hỏi', required=True)
    supporter = fields.Many2one('res.users', string='Nhân Viên Hỗ Trợ')
    answer = fields.Text(string='Câu Trả Lời')

    @api.model
    def _create_feedback_template(self):
        IrModel = self.env['ir.model']
        model_id = IrModel.search([('model', '=', 'khach_hang.feedback')], limit=1).id
        if not self.env['mail.template'].search([('name', '=', 'Phản Hồi Từ Nhân Viên Hỗ Trợ')]):
            self.env['mail.template'].create({
                'name': 'Phản Hồi Từ Nhân Viên Hỗ Trợ',
                'model_id': model_id,
                'email_from': '${object.supporter.email_formatted}',
                'email_to': '${object.customer_id.email}',
                'subject': 'Phản Hồi Cho Câu Hỏi Của Bạn',
                'body_html': """
                    <p>Xin chào ${object.customer_id.name},</p>
                    <p>Chúng tôi đã nhận được câu hỏi của bạn: <strong>${object.question}</strong></p>
                    <p>Đây là câu trả lời từ nhân viên hỗ trợ ${object.supporter.name}:<br/>
                    ${object.answer}</p>
                    <p>Trân trọng,<br/>Đội ngũ hỗ trợ</p>
                """,
            })

    @api.model
    def create(self, vals):
        if not self.env['mail.template'].search([('name', '=', 'Phản Hồi Từ Nhân Viên Hỗ Trợ')]):
            self._create_feedback_template()
        feedback = super(Feedback, self).create(vals)
        return feedback

    def write(self, vals):
        result = super(Feedback, self).write(vals)
        if 'answer' in vals and vals['answer'] and self.customer_id.email:
            self._send_feedback_email()
        return result

    def _send_feedback_email(self):
        template = self.env.ref('khach_hang.mail_template_feedback_response')
        template.send_mail(self.id, force_send=True)