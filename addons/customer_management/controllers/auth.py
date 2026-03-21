# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

# Secret key for JWT - In production, use environment variable
JWT_SECRET_KEY = 'odoo_customer_management_secret_key_2026'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def generate_token(customer_id, username):
    """Generate JWT token for customer"""
    payload = {
        'customer_id': customer_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_customer():
    """Get current customer from JWT token in Authorization header"""
    auth_header = request.httprequest.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    payload = verify_token(token)
    if not payload:
        return None
    
    customer = request.env['khach_hang.customer'].sudo().browse(payload.get('customer_id'))
    if not customer.exists():
        return None
    
    return customer


class CustomerAuthAPI(http.Controller):
    """Customer Authentication API with JWT"""

    @http.route('/api/auth/register', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def register(self, **kwargs):
        """Register a new customer account"""
        try:
            data = request.jsonrequest or {}
            
            # Validate required fields
            required_fields = ['username', 'password', 'name']
            for field in required_fields:
                if not data.get(field):
                    return {
                        'success': False,
                        'error': f'Thiếu trường bắt buộc: {field}'
                    }
            
            username = data.get('username').strip().lower()
            password = data.get('password')
            
            # Validate username
            if len(username) < 3:
                return {
                    'success': False,
                    'error': 'Tên đăng nhập phải có ít nhất 3 ký tự'
                }
            
            # Validate password
            if len(password) < 6:
                return {
                    'success': False,
                    'error': 'Mật khẩu phải có ít nhất 6 ký tự'
                }
            
            # Check if username already exists
            existing = request.env['khach_hang.customer'].sudo().search([
                ('username', '=', username)
            ], limit=1)
            if existing:
                return {
                    'success': False,
                    'error': 'Tên đăng nhập đã tồn tại'
                }
            
            # Create customer
            customer = request.env['khach_hang.customer'].sudo().create({
                'name': data.get('name'),
                'username': username,
                'email': data.get('email'),
                'phone': data.get('phone'),
                'address': data.get('address'),
            })
            
            # Set password
            customer.set_password(password)
            
            # Generate token
            token = generate_token(customer.id, customer.username)
            
            return {
                'success': True,
                'message': 'Đăng ký thành công!',
                'data': {
                    'customer': {
                        'id': customer.id,
                        'name': customer.name,
                        'username': customer.username,
                        'email': customer.email,
                        'phone': customer.phone
                    },
                    'token': token,
                    'expires_in': JWT_EXPIRATION_HOURS * 3600
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def login(self, **kwargs):
        """Login with username and password"""
        try:
            data = request.jsonrequest or {}
            
            username = data.get('username', '').strip().lower()
            password = data.get('password', '')
            
            if not username or not password:
                return {
                    'success': False,
                    'error': 'Vui lòng nhập tên đăng nhập và mật khẩu'
                }
            
            # Find customer by username
            customer = request.env['khach_hang.customer'].sudo().search([
                ('username', '=', username)
            ], limit=1)
            
            if not customer:
                return {
                    'success': False,
                    'error': 'Tên đăng nhập hoặc mật khẩu không đúng'
                }
            
            # Verify password
            if not customer._verify_password(password):
                return {
                    'success': False,
                    'error': 'Tên đăng nhập hoặc mật khẩu không đúng'
                }
            
            # Generate token
            token = generate_token(customer.id, customer.username)
            
            return {
                'success': True,
                'message': 'Đăng nhập thành công!',
                'data': {
                    'customer': {
                        'id': customer.id,
                        'name': customer.name,
                        'username': customer.username,
                        'email': customer.email,
                        'phone': customer.phone
                    },
                    'token': token,
                    'expires_in': JWT_EXPIRATION_HOURS * 3600
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/auth/me', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def get_profile(self, **kwargs):
        """Get current customer profile (requires authentication)"""
        try:
            customer = get_current_customer()
            if not customer:
                return {
                    'success': False,
                    'error': 'Unauthorized. Vui lòng đăng nhập.'
                }
            
            return {
                'success': True,
                'data': {
                    'id': customer.id,
                    'name': customer.name,
                    'username': customer.username,
                    'email': customer.email,
                    'phone': customer.phone,
                    'address': customer.address,
                    'order_count': customer.order_count
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/auth/update-profile', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def update_profile(self, **kwargs):
        """Update current customer profile (requires authentication)"""
        try:
            customer = get_current_customer()
            if not customer:
                return {
                    'success': False,
                    'error': 'Unauthorized. Vui lòng đăng nhập.'
                }
            
            data = request.jsonrequest or {}
            
            update_vals = {}
            for field in ['name', 'email', 'phone', 'address']:
                if field in data:
                    update_vals[field] = data[field]
            
            if update_vals:
                customer.write(update_vals)
            
            return {
                'success': True,
                'message': 'Cập nhật thông tin thành công!',
                'data': {
                    'id': customer.id,
                    'name': customer.name,
                    'username': customer.username,
                    'email': customer.email,
                    'phone': customer.phone,
                    'address': customer.address
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/auth/change-password', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def change_password(self, **kwargs):
        """Change password for current customer (requires authentication)"""
        try:
            customer = get_current_customer()
            if not customer:
                return {
                    'success': False,
                    'error': 'Unauthorized. Vui lòng đăng nhập.'
                }
            
            data = request.jsonrequest or {}
            
            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')
            
            if not old_password or not new_password:
                return {
                    'success': False,
                    'error': 'Vui lòng nhập mật khẩu cũ và mật khẩu mới'
                }
            
            # Verify old password
            if not customer._verify_password(old_password):
                return {
                    'success': False,
                    'error': 'Mật khẩu cũ không đúng'
                }
            
            # Validate new password
            if len(new_password) < 6:
                return {
                    'success': False,
                    'error': 'Mật khẩu mới phải có ít nhất 6 ký tự'
                }
            
            # Set new password
            customer.set_password(new_password)
            
            return {
                'success': True,
                'message': 'Đổi mật khẩu thành công!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/auth/my-orders', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def get_my_orders(self, **kwargs):
        """Get orders for current customer (requires authentication)"""
        try:
            customer = get_current_customer()
            if not customer:
                return {
                    'success': False,
                    'error': 'Unauthorized. Vui lòng đăng nhập.'
                }
            
            orders = []
            for order in customer.order_ids:
                orders.append({
                    'id': order.id,
                    'name': order.name,
                    'total_amount': order.total_amount,
                    'state': order.state,
                    'date_order': order.date_order.isoformat() if order.date_order else None,
                    'delivery_date': order.delivery_date.isoformat() if order.delivery_date else None,
                    'products': [{'id': p.id, 'name': p.name, 'price': p.price} for p in order.product_ids]
                })
            
            return {
                'success': True,
                'data': orders
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/api/auth/verify', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def verify_token_endpoint(self, **kwargs):
        """Verify if token is still valid"""
        try:
            customer = get_current_customer()
            if not customer:
                return {
                    'success': False,
                    'valid': False,
                    'error': 'Token không hợp lệ hoặc đã hết hạn'
                }
            
            return {
                'success': True,
                'valid': True,
                'data': {
                    'customer_id': customer.id,
                    'username': customer.username
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
