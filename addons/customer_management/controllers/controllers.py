from odoo import http
from odoo.http import request

class CustomerManagementController(http.Controller):

    @http.route('/customer_management/customers', type='http', auth='user', website=True)
    def customer_list(self):
        customers = request.env['cm.customer'].search([])
        return request.render('customer_management.customer_list_template', {'customers': customers})

    @http.route('/customer_management/products', type='http', auth='user', website=True)
    def product_list(self):
        products = request.env['cm.product'].search([])
        return request.render('customer_management.product_list_template', {'products': products})

    @http.route('/customer_management/orders', type='http', auth='user', website=True)
    def order_list(self):
        orders = request.env['cm.order'].search([])
        return request.render('customer_management.order_list_template', {'orders': orders})

    @http.route('/customer_management/feedback', type='http', auth='user', website=True)
    def feedback_list(self):
        feedbacks = request.env['cm.feedback'].search([])
        return request.render('customer_management.feedback_list_template', {'feedbacks': feedbacks})

    @http.route('/customer_management/potential_customers', type='http', auth='user', website=True)
    def potential_customer_list(self):
        potential_customers = request.env['cm.potential.customer'].search([])
        return request.render('customer_management.potential_customer_list_template', {'potential_customers': potential_customers})

    @http.route('/customer_management/care', type='http', auth='user', website=True)
    def care_list(self):
        care_records = request.env['cm.care'].search([])
        return request.render('customer_management.care_list_template', {'care_records': care_records})