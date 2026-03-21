#!/usr/bin/env python3
"""
Script để reset mật khẩu admin trong Odoo
"""

import sys
import os

# Add Odoo to path
sys.path.append('/home/quoc/16-06-N01')

import odoo
from odoo import api, SUPERUSER_ID

# Cấu hình
DB_NAME = 'odoo15'
NEW_PASSWORD = 'admin'  # Mật khẩu mới

def reset_admin_password():
    """Reset mật khẩu của user admin"""
    
    # Load Odoo config
    odoo.tools.config.parse_config(['-c', '/home/quoc/16-06-N01/odoo.conf'])
    
    # Connect to database
    with api.Environment.manage():
        registry = odoo.registry(DB_NAME)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Tìm user admin
            admin_user = env['res.users'].search([('login', '=', 'admin')], limit=1)
            
            if not admin_user:
                print("❌ Không tìm thấy user admin!")
                return False
            
            # Reset password
            admin_user.write({'password': NEW_PASSWORD})
            cr.commit()
            
            print(f"✅ Đã reset mật khẩu thành công!")
            print(f"📧 Email/Login: admin")
            print(f"🔑 Mật khẩu mới: {NEW_PASSWORD}")
            print(f"\n🌐 Đăng nhập tại: http://localhost:8069")
            
            return True

if __name__ == '__main__':
    print("🔄 Đang reset mật khẩu admin...")
    reset_admin_password()
