from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime, date


def json_response(data, status=200):
    """Helper function to create JSON response"""
    return Response(
        json.dumps(data, default=str, ensure_ascii=False),
        status=status,
        content_type='application/json; charset=utf-8'
    )


def serialize_record(record, fields_list):
    """Serialize a single record to dictionary"""
    result = {'id': record.id}
    for field in fields_list:
        value = record[field]
        if hasattr(value, 'id'):  # Many2one field
            result[field] = {'id': value.id, 'name': value.name} if value else None
        elif hasattr(value, 'ids'):  # One2many or Many2many field
            result[field] = [{'id': r.id, 'name': r.name if hasattr(r, 'name') else str(r.id)} for r in value]
        elif isinstance(value, (datetime, date)):
            result[field] = value.isoformat() if value else None
        else:
            result[field] = value
    return result


class CustomerManagementAPI(http.Controller):
    """Public API for Customer Management module"""

    # ==================== CUSTOMER API ====================
    
    @http.route('/api/customers', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_customers(self, **kwargs):
        """Get all customers"""
        try:
            customers = request.env['khach_hang.customer'].sudo().search([])
            fields = ['name', 'email', 'phone', 'address', 'order_count']
            data = [serialize_record(c, fields) for c in customers]
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/customers/<int:customer_id>', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_customer(self, customer_id, **kwargs):
        """Get a specific customer by ID"""
        try:
            customer = request.env['khach_hang.customer'].sudo().browse(customer_id)
            if not customer.exists():
                return json_response({'success': False, 'error': 'Customer not found'}, 404)
            
            fields = ['name', 'email', 'phone', 'address', 'order_count']
            data = serialize_record(customer, fields)
            
            # Include orders
            data['orders'] = [{
                'id': o.id,
                'name': o.name,
                'total_amount': o.total_amount,
                'state': o.state,
                'date_order': o.date_order.isoformat() if o.date_order else None
            } for o in customer.order_ids]
            
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/customers', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_customer(self, **kwargs):
        """Create a new customer"""
        try:
            data = request.jsonrequest
            required_fields = ['name']
            for field in required_fields:
                if field not in data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            customer = request.env['khach_hang.customer'].sudo().create({
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'address': data.get('address'),
            })
            
            return {'success': True, 'data': {'id': customer.id, 'name': customer.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/customers/<int:customer_id>', type='json', auth='none', methods=['PUT'], csrf=False, cors='*')
    def update_customer(self, customer_id, **kwargs):
        """Update a customer"""
        try:
            customer = request.env['khach_hang.customer'].sudo().browse(customer_id)
            if not customer.exists():
                return {'success': False, 'error': 'Customer not found'}
            
            data = request.jsonrequest
            update_vals = {}
            for field in ['name', 'email', 'phone', 'address']:
                if field in data:
                    update_vals[field] = data[field]
            
            customer.write(update_vals)
            return {'success': True, 'data': {'id': customer.id, 'name': customer.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/customers/<int:customer_id>', type='json', auth='none', methods=['DELETE'], csrf=False, cors='*')
    def delete_customer(self, customer_id, **kwargs):
        """Delete a customer"""
        try:
            customer = request.env['khach_hang.customer'].sudo().browse(customer_id)
            if not customer.exists():
                return {'success': False, 'error': 'Customer not found'}
            
            customer.unlink()
            return {'success': True, 'message': 'Customer deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== PRODUCT API ====================
    
    @http.route('/api/products', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_products(self, **kwargs):
        """Get all products"""
        try:
            products = request.env['khach_hang.product'].sudo().search([])
            fields = ['name', 'price', 'description', 'category_id', 'stock_quantity', 'stock_alert_threshold']
            data = [serialize_record(p, fields) for p in products]
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/products/<int:product_id>', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_product(self, product_id, **kwargs):
        """Get a specific product by ID"""
        try:
            product = request.env['khach_hang.product'].sudo().browse(product_id)
            if not product.exists():
                return json_response({'success': False, 'error': 'Product not found'}, 404)
            
            fields = ['name', 'price', 'description', 'category_id', 'stock_quantity', 'stock_alert_threshold']
            data = serialize_record(product, fields)
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/products', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_product(self, **kwargs):
        """Create a new product"""
        try:
            data = request.jsonrequest
            required_fields = ['name', 'price']
            for field in required_fields:
                if field not in data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            product = request.env['khach_hang.product'].sudo().create({
                'name': data.get('name'),
                'price': data.get('price'),
                'description': data.get('description'),
                'category_id': data.get('category_id'),
                'stock_quantity': data.get('stock_quantity', 0),
                'stock_alert_threshold': data.get('stock_alert_threshold', 10),
            })
            
            return {'success': True, 'data': {'id': product.id, 'name': product.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/products/<int:product_id>', type='json', auth='none', methods=['PUT'], csrf=False, cors='*')
    def update_product(self, product_id, **kwargs):
        """Update a product"""
        try:
            product = request.env['khach_hang.product'].sudo().browse(product_id)
            if not product.exists():
                return {'success': False, 'error': 'Product not found'}
            
            data = request.jsonrequest
            update_vals = {}
            for field in ['name', 'price', 'description', 'category_id', 'stock_quantity', 'stock_alert_threshold']:
                if field in data:
                    update_vals[field] = data[field]
            
            product.write(update_vals)
            return {'success': True, 'data': {'id': product.id, 'name': product.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/products/<int:product_id>', type='json', auth='none', methods=['DELETE'], csrf=False, cors='*')
    def delete_product(self, product_id, **kwargs):
        """Delete a product"""
        try:
            product = request.env['khach_hang.product'].sudo().browse(product_id)
            if not product.exists():
                return {'success': False, 'error': 'Product not found'}
            
            product.unlink()
            return {'success': True, 'message': 'Product deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== PRODUCT CATEGORY API ====================
    
    @http.route('/api/product-categories', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_product_categories(self, **kwargs):
        """Get all product categories"""
        try:
            categories = request.env['khach_hang.product.category'].sudo().search([])
            fields = ['name', 'description']
            data = [serialize_record(c, fields) for c in categories]
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/product-categories', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_product_category(self, **kwargs):
        """Create a new product category"""
        try:
            data = request.jsonrequest
            if 'name' not in data:
                return {'success': False, 'error': 'Missing required field: name'}
            
            category = request.env['khach_hang.product.category'].sudo().create({
                'name': data.get('name'),
                'description': data.get('description'),
            })
            
            return {'success': True, 'data': {'id': category.id, 'name': category.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== ORDER API ====================
    
    @http.route('/api/orders', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_orders(self, **kwargs):
        """Get all orders"""
        try:
            orders = request.env['khach_hang.order'].sudo().search([])
            data = []
            for order in orders:
                order_data = {
                    'id': order.id,
                    'name': order.name,
                    'customer': {'id': order.customer_id.id, 'name': order.customer_id.name} if order.customer_id else None,
                    'products': [{'id': p.id, 'name': p.name, 'price': p.price} for p in order.product_ids],
                    'total_amount': order.total_amount,
                    'date_order': order.date_order.isoformat() if order.date_order else None,
                    'state': order.state,
                    'delivery_date': order.delivery_date.isoformat() if order.delivery_date else None,
                    'delivery_days': order.delivery_days,
                }
                data.append(order_data)
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/orders/<int:order_id>', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_order(self, order_id, **kwargs):
        """Get a specific order by ID"""
        try:
            order = request.env['khach_hang.order'].sudo().browse(order_id)
            if not order.exists():
                return json_response({'success': False, 'error': 'Order not found'}, 404)
            
            data = {
                'id': order.id,
                'name': order.name,
                'customer': {'id': order.customer_id.id, 'name': order.customer_id.name} if order.customer_id else None,
                'products': [{'id': p.id, 'name': p.name, 'price': p.price} for p in order.product_ids],
                'total_amount': order.total_amount,
                'date_order': order.date_order.isoformat() if order.date_order else None,
                'state': order.state,
                'delivery_date': order.delivery_date.isoformat() if order.delivery_date else None,
                'delivery_days': order.delivery_days,
            }
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/orders', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_order(self, **kwargs):
        """Create a new order"""
        try:
            data = request.jsonrequest
            required_fields = ['name', 'customer_id']
            for field in required_fields:
                if field not in data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            order_vals = {
                'name': data.get('name'),
                'customer_id': data.get('customer_id'),
                'state': data.get('state', 'draft'),
            }
            
            if 'product_ids' in data:
                order_vals['product_ids'] = [(6, 0, data.get('product_ids', []))]
            
            if 'delivery_date' in data:
                order_vals['delivery_date'] = data.get('delivery_date')
            
            order = request.env['khach_hang.order'].sudo().create(order_vals)
            
            return {'success': True, 'data': {'id': order.id, 'name': order.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/orders/<int:order_id>', type='json', auth='none', methods=['PUT'], csrf=False, cors='*')
    def update_order(self, order_id, **kwargs):
        """Update an order"""
        try:
            order = request.env['khach_hang.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Order not found'}
            
            data = request.jsonrequest
            update_vals = {}
            
            for field in ['name', 'customer_id', 'state', 'delivery_date']:
                if field in data:
                    update_vals[field] = data[field]
            
            if 'product_ids' in data:
                update_vals['product_ids'] = [(6, 0, data.get('product_ids', []))]
            
            order.write(update_vals)
            return {'success': True, 'data': {'id': order.id, 'name': order.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/orders/<int:order_id>', type='json', auth='none', methods=['DELETE'], csrf=False, cors='*')
    def delete_order(self, order_id, **kwargs):
        """Delete an order"""
        try:
            order = request.env['khach_hang.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Order not found'}
            
            order.unlink()
            return {'success': True, 'message': 'Order deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/orders/<int:order_id>/confirm', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def confirm_order(self, order_id, **kwargs):
        """Confirm an order"""
        try:
            order = request.env['khach_hang.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Order not found'}
            
            order.action_confirm()
            return {'success': True, 'data': {'id': order.id, 'state': order.state}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/orders/<int:order_id>/ship', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def ship_order(self, order_id, **kwargs):
        """Set order to shipping"""
        try:
            order = request.env['khach_hang.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Order not found'}
            
            order.action_ship()
            return {'success': True, 'data': {'id': order.id, 'state': order.state}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/orders/<int:order_id>/done', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def complete_order(self, order_id, **kwargs):
        """Complete an order"""
        try:
            order = request.env['khach_hang.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Order not found'}
            
            order.action_done()
            return {'success': True, 'data': {'id': order.id, 'state': order.state}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/orders/<int:order_id>/cancel', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def cancel_order(self, order_id, **kwargs):
        """Cancel an order"""
        try:
            order = request.env['khach_hang.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Order not found'}
            
            order.action_cancel()
            return {'success': True, 'data': {'id': order.id, 'state': order.state}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== FEEDBACK API ====================
    
    @http.route('/api/feedbacks', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_feedbacks(self, **kwargs):
        """Get all feedbacks"""
        try:
            feedbacks = request.env['khach_hang.feedback'].sudo().search([])
            data = []
            for f in feedbacks:
                feedback_data = {
                    'id': f.id,
                    'customer': {'id': f.customer_id.id, 'name': f.customer_id.name} if f.customer_id else None,
                    'question': f.question,
                    'supporter': {'id': f.supporter.id, 'name': f.supporter.name} if f.supporter else None,
                    'answer': f.answer,
                }
                data.append(feedback_data)
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/feedbacks/<int:feedback_id>', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_feedback(self, feedback_id, **kwargs):
        """Get a specific feedback by ID"""
        try:
            feedback = request.env['khach_hang.feedback'].sudo().browse(feedback_id)
            if not feedback.exists():
                return json_response({'success': False, 'error': 'Feedback not found'}, 404)
            
            data = {
                'id': feedback.id,
                'customer': {'id': feedback.customer_id.id, 'name': feedback.customer_id.name} if feedback.customer_id else None,
                'question': feedback.question,
                'supporter': {'id': feedback.supporter.id, 'name': feedback.supporter.name} if feedback.supporter else None,
                'answer': feedback.answer,
            }
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/feedbacks', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_feedback(self, **kwargs):
        """Create a new feedback"""
        try:
            data = request.jsonrequest
            required_fields = ['customer_id', 'question']
            for field in required_fields:
                if field not in data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            feedback = request.env['khach_hang.feedback'].sudo().create({
                'customer_id': data.get('customer_id'),
                'question': data.get('question'),
                'supporter': data.get('supporter_id'),
                'answer': data.get('answer'),
            })
            
            return {'success': True, 'data': {'id': feedback.id}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/feedbacks/<int:feedback_id>', type='json', auth='none', methods=['PUT'], csrf=False, cors='*')
    def update_feedback(self, feedback_id, **kwargs):
        """Update a feedback (typically to add answer)"""
        try:
            feedback = request.env['khach_hang.feedback'].sudo().browse(feedback_id)
            if not feedback.exists():
                return {'success': False, 'error': 'Feedback not found'}
            
            data = request.jsonrequest
            update_vals = {}
            
            for field in ['question', 'answer']:
                if field in data:
                    update_vals[field] = data[field]
            
            if 'supporter_id' in data:
                update_vals['supporter'] = data['supporter_id']
            
            feedback.write(update_vals)
            return {'success': True, 'data': {'id': feedback.id}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/feedbacks/<int:feedback_id>', type='json', auth='none', methods=['DELETE'], csrf=False, cors='*')
    def delete_feedback(self, feedback_id, **kwargs):
        """Delete a feedback"""
        try:
            feedback = request.env['khach_hang.feedback'].sudo().browse(feedback_id)
            if not feedback.exists():
                return {'success': False, 'error': 'Feedback not found'}
            
            feedback.unlink()
            return {'success': True, 'message': 'Feedback deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== CARE ACTIVITY API ====================
    
    @http.route('/api/care-activities', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_care_activities(self, **kwargs):
        """Get all care activities"""
        try:
            activities = request.env['khach_hang.care_activity'].sudo().search([])
            data = []
            for a in activities:
                activity_data = {
                    'id': a.id,
                    'customer': {'id': a.customer_id.id, 'name': a.customer_id.name} if a.customer_id else None,
                    'care_date': a.care_date.isoformat() if a.care_date else None,
                    'care_staff': {'id': a.care_staff.id, 'name': a.care_staff.name} if a.care_staff else None,
                    'contact_method': a.contact_method,
                    'notes': a.notes,
                }
                data.append(activity_data)
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/care-activities/<int:activity_id>', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_care_activity(self, activity_id, **kwargs):
        """Get a specific care activity by ID"""
        try:
            activity = request.env['khach_hang.care_activity'].sudo().browse(activity_id)
            if not activity.exists():
                return json_response({'success': False, 'error': 'Care activity not found'}, 404)
            
            data = {
                'id': activity.id,
                'customer': {'id': activity.customer_id.id, 'name': activity.customer_id.name} if activity.customer_id else None,
                'care_date': activity.care_date.isoformat() if activity.care_date else None,
                'care_staff': {'id': activity.care_staff.id, 'name': activity.care_staff.name} if activity.care_staff else None,
                'contact_method': activity.contact_method,
                'notes': activity.notes,
            }
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/care-activities', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_care_activity(self, **kwargs):
        """Create a new care activity"""
        try:
            data = request.jsonrequest
            required_fields = ['customer_id', 'care_date', 'contact_method']
            for field in required_fields:
                if field not in data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            activity = request.env['khach_hang.care_activity'].sudo().create({
                'customer_id': data.get('customer_id'),
                'care_date': data.get('care_date'),
                'care_staff': data.get('care_staff_id'),
                'contact_method': data.get('contact_method'),
                'notes': data.get('notes'),
            })
            
            return {'success': True, 'data': {'id': activity.id}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/care-activities/<int:activity_id>', type='json', auth='none', methods=['PUT'], csrf=False, cors='*')
    def update_care_activity(self, activity_id, **kwargs):
        """Update a care activity"""
        try:
            activity = request.env['khach_hang.care_activity'].sudo().browse(activity_id)
            if not activity.exists():
                return {'success': False, 'error': 'Care activity not found'}
            
            data = request.jsonrequest
            update_vals = {}
            
            for field in ['customer_id', 'care_date', 'contact_method', 'notes']:
                if field in data:
                    update_vals[field] = data[field]
            
            if 'care_staff_id' in data:
                update_vals['care_staff'] = data['care_staff_id']
            
            activity.write(update_vals)
            return {'success': True, 'data': {'id': activity.id}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/care-activities/<int:activity_id>', type='json', auth='none', methods=['DELETE'], csrf=False, cors='*')
    def delete_care_activity(self, activity_id, **kwargs):
        """Delete a care activity"""
        try:
            activity = request.env['khach_hang.care_activity'].sudo().browse(activity_id)
            if not activity.exists():
                return {'success': False, 'error': 'Care activity not found'}
            
            activity.unlink()
            return {'success': True, 'message': 'Care activity deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== POTENTIAL CUSTOMER API ====================
    
    @http.route('/api/potential-customers', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_potential_customers(self, **kwargs):
        """Get all potential customers"""
        try:
            customers = request.env['khach_hang.potential_customer'].sudo().search([])
            fields = ['name', 'product_type', 'contact_info', 'source', 'interest_level', 'contact_date', 'notes', 'potential_value']
            data = [serialize_record(c, fields) for c in customers]
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/potential-customers/<int:customer_id>', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_potential_customer(self, customer_id, **kwargs):
        """Get a specific potential customer by ID"""
        try:
            customer = request.env['khach_hang.potential_customer'].sudo().browse(customer_id)
            if not customer.exists():
                return json_response({'success': False, 'error': 'Potential customer not found'}, 404)
            
            fields = ['name', 'product_type', 'contact_info', 'source', 'interest_level', 'contact_date', 'notes', 'potential_value']
            data = serialize_record(customer, fields)
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)

    @http.route('/api/potential-customers', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_potential_customer(self, **kwargs):
        """Create a new potential customer"""
        try:
            data = request.jsonrequest
            if 'name' not in data:
                return {'success': False, 'error': 'Missing required field: name'}
            
            customer = request.env['khach_hang.potential_customer'].sudo().create({
                'name': data.get('name'),
                'product_type': data.get('product_type'),
                'contact_info': data.get('contact_info'),
                'source': data.get('source', 'self_search'),
                'interest_level': data.get('interest_level', 'medium'),
                'contact_date': data.get('contact_date'),
                'notes': data.get('notes'),
                'potential_value': data.get('potential_value', 0.0),
            })
            
            return {'success': True, 'data': {'id': customer.id, 'name': customer.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/potential-customers/<int:customer_id>', type='json', auth='none', methods=['PUT'], csrf=False, cors='*')
    def update_potential_customer(self, customer_id, **kwargs):
        """Update a potential customer"""
        try:
            customer = request.env['khach_hang.potential_customer'].sudo().browse(customer_id)
            if not customer.exists():
                return {'success': False, 'error': 'Potential customer not found'}
            
            data = request.jsonrequest
            update_vals = {}
            
            for field in ['name', 'product_type', 'contact_info', 'source', 'interest_level', 'contact_date', 'notes', 'potential_value']:
                if field in data:
                    update_vals[field] = data[field]
            
            customer.write(update_vals)
            return {'success': True, 'data': {'id': customer.id, 'name': customer.name}}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/potential-customers/<int:customer_id>', type='json', auth='none', methods=['DELETE'], csrf=False, cors='*')
    def delete_potential_customer(self, customer_id, **kwargs):
        """Delete a potential customer"""
        try:
            customer = request.env['khach_hang.potential_customer'].sudo().browse(customer_id)
            if not customer.exists():
                return {'success': False, 'error': 'Potential customer not found'}
            
            customer.unlink()
            return {'success': True, 'message': 'Potential customer deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/api/potential-customers/<int:customer_id>/convert', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def convert_potential_customer(self, customer_id, **kwargs):
        """Convert a potential customer to a regular customer"""
        try:
            potential_customer = request.env['khach_hang.potential_customer'].sudo().browse(customer_id)
            if not potential_customer.exists():
                return {'success': False, 'error': 'Potential customer not found'}
            
            # Create new customer
            customer = request.env['khach_hang.customer'].sudo().create({
                'name': potential_customer.name,
                'email': potential_customer.contact_info if '@' in (potential_customer.contact_info or '') else False,
                'phone': potential_customer.contact_info if '@' not in (potential_customer.contact_info or '') else False,
                'address': potential_customer.notes or False,
            })
            
            # Update notes on potential customer
            potential_customer.write({'notes': f'Đã chuyển thành khách hàng {customer.id}'})
            
            return {
                'success': True,
                'data': {
                    'new_customer_id': customer.id,
                    'new_customer_name': customer.name
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== STATISTICS API ====================
    
    @http.route('/api/statistics/overview', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_statistics_overview(self, **kwargs):
        """Get overview statistics"""
        try:
            Customer = request.env['khach_hang.customer'].sudo()
            Order = request.env['khach_hang.order'].sudo()
            Product = request.env['khach_hang.product'].sudo()
            PotentialCustomer = request.env['khach_hang.potential_customer'].sudo()
            
            # Count statistics
            total_customers = Customer.search_count([])
            total_orders = Order.search_count([])
            total_products = Product.search_count([])
            total_potential_customers = PotentialCustomer.search_count([])
            
            # Order statistics by state
            orders_by_state = {}
            for state in ['draft', 'confirmed', 'shipping', 'done', 'cancel']:
                orders_by_state[state] = Order.search_count([('state', '=', state)])
            
            # Total revenue (from completed orders)
            completed_orders = Order.search([('state', '=', 'done')])
            total_revenue = sum(order.total_amount for order in completed_orders)
            
            # Low stock products
            low_stock_products = Product.search_count([
                ('stock_quantity', '<', 10)
            ])
            
            data = {
                'total_customers': total_customers,
                'total_orders': total_orders,
                'total_products': total_products,
                'total_potential_customers': total_potential_customers,
                'orders_by_state': orders_by_state,
                'total_revenue': total_revenue,
                'low_stock_products': low_stock_products,
            }
            
            return json_response({'success': True, 'data': data})
        except Exception as e:
            return json_response({'success': False, 'error': str(e)}, 500)
