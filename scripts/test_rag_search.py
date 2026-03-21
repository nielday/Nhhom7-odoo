#!/usr/bin/env python3
"""
Test RAG document retrieval directly
"""
import xmlrpc.client

ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'odoo'
ODOO_USERNAME = 'admin'
ODOO_PASSWORD = 'admin'

def test_rag_search(query):
    """Test document search"""
    try:
        # Connect
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("❌ Login failed")
            return
        
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        print(f"\n🔍 Testing search for: '{query}'")
        print("="*60)
        
        # Test 1: Simple search
        print("\n1. Simple full query search:")
        docs = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'chatbot.knowledge.base', 'search_read',
            [[
                ('active', '=', True),
                '|', '|',
                ('name', 'ilike', query),
                ('content_plain', 'ilike', query),
                ('keywords', 'ilike', query)
            ]],
            {'fields': ['name', 'keywords'], 'limit': 3}
        )
        print(f"Found {len(docs)} documents:")
        for doc in docs:
            print(f"  - {doc['name']}")
            print(f"    Keywords: {doc['keywords']}")
        
        # Test 2: Word-by-word search
        print("\n2. Word-by-word search:")
        words = query.lower().split()
        print(f"Query words: {words}")
        
        for word in words:
            if len(word) >= 2:
                docs = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'chatbot.knowledge.base', 'search_read',
                    [[
                        ('active', '=', True),
                        '|', '|',
                        ('name', 'ilike', word),
                        ('content_plain', 'ilike', word),
                        ('keywords', 'ilike', word)
                    ]],
                    {'fields': ['name'], 'limit': 5}
                )
                print(f"\n  Word '{word}' found {len(docs)} docs:")
                for doc in docs:
                    print(f"    - {doc['name']}")
        
        # Test 3: Check all KB entries
        print("\n3. All Knowledge Base entries:")
        all_docs = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'chatbot.knowledge.base', 'search_read',
            [[('active', '=', True)]],
            {'fields': ['name', 'keywords', 'category']}
        )
        print(f"Total: {len(all_docs)} entries")
        for doc in all_docs:
            print(f"  - [{doc['category']}] {doc['name']}")
            print(f"    Keywords: {doc['keywords']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "giờ làm việc"
    test_rag_search(query)
