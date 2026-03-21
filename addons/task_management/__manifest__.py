# -*- coding: utf-8 -*-
{
    'name': "Task Management",
    'summary': "Hệ thống quản lý công việc và tiến độ dự án",
    'description': """
        Module quản lý công việc chuyên nghiệp (Final Project):
        - Quản lý danh sách công việc (Tasks)
        - Giao diện Kanban (Kéo thả trạng thái)
        - Tích hợp với Module Customer Management
        - Theo dõi hạn chót (Deadline) & KPI
        - Báo cáo tiến độ
        - Tự động tạo Task khi có đơn hàng mới
    """,
    'author': "Vũ Minh Quốc",
    'category': 'Project Management',
    'version': '1.1',
    'license': 'LGPL-3',

    'depends': ['base', 'mail', 'customer_management', 'nhan_su'], 
    
    'data': [
        'security/ir.model.access.csv',
        'views/task_view.xml',
        'views/order_inherit_view.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'application': True,
    'installable': True,
}