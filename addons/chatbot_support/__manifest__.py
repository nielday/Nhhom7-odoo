# -*- coding: utf-8 -*-
{
    'name': "AI Chatbot Support (RAG)",
    'summary': "Chatbot tư vấn khách hàng thông minh với Gemini AI & RAG",
    'description': """
        Module Chatbot hỗ trợ khách hàng tự động:
        - Sử dụng Gemini AI (Google) để sinh câu trả lời tự nhiên
        - RAG (Retrieval-Augmented Generation) để truy xuất thông tin chính xác
        - Tích hợp với Customer Management & Product Database
        - Lưu trữ lịch sử hội thoại
        - Quản lý Knowledge Base (FAQ, Product Info)
        - API endpoints cho web chat widget
    """,
    'author': "Vũ Minh Quốc",
    'category': 'Customer Support',
    'version': '1.0',
    'license': 'LGPL-3',

    'depends': ['base', 'mail', 'customer_management'],
    
    'data': [
        'security/ir.model.access.csv',
        'data/demo_data.xml',
        'views/knowledge_base_view.xml',
        'views/conversation_view.xml',
        'views/chatbot_config_view.xml',
        'views/menu.xml',
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
