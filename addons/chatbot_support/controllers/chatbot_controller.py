# -*- coding: utf-8 -*-
import json
import logging
import requests
from datetime import datetime
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ChatbotController(http.Controller):
    
    @http.route('/chatbot/api/chat', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def chat(self, message, session_id=None, partner_id=None, **kwargs):
        """
        Main chat endpoint
        
        Args:
            message (str): User's message
            session_id (str): Session ID for conversation tracking
            partner_id (int): Optional customer ID
        
        Returns:
            dict: {
                'response': str,
                'conversation_id': int,
                'message_id': int,
                'success': bool
            }
        """
        try:
            # Get or create conversation
            conversation = self._get_or_create_conversation(session_id, partner_id, kwargs)
            
            # Save user message
            user_message = request.env['chatbot.message'].sudo().create({
                'conversation_id': conversation.id,
                'message_type': 'user',
                'content': message,
            })
            
            # Get chatbot response using RAG
            bot_response, metadata = self._get_bot_response(message, conversation)
            
            # Save bot message
            bot_message = request.env['chatbot.message'].sudo().create({
                'conversation_id': conversation.id,
                'message_type': 'bot',
                'content': bot_response,
                'retrieved_docs': json.dumps(metadata.get('retrieved_docs', [])),
                'confidence_score': metadata.get('confidence_score', 0.0),
                'model_used': metadata.get('model_used', 'llama-3.3-70b-versatile'),
                'response_time': metadata.get('response_time', 0.0),
            })
            
            return {
                'success': True,
                'response': bot_response,
                'conversation_id': conversation.id,
                'message_id': bot_message.id,
                'metadata': metadata
            }
            
        except Exception as e:
            _logger.error(f"Chatbot error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'response': 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.'
            }
    
    @http.route('/chatbot/api/welcome', type='json', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_welcome_message(self, **kwargs):
        """Get welcome message from config"""
        try:
            config = request.env['chatbot.config'].sudo().get_active_config()
            return {
                'success': True,
                'message': config.welcome_message
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Xin chào! Tôi có thể giúp gì cho bạn?'
            }
    
    @http.route('/chatbot/api/rate', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def rate_conversation(self, conversation_id, rating, feedback=None, **kwargs):
        """Rate a conversation"""
        try:
            conversation = request.env['chatbot.conversation'].sudo().browse(conversation_id)
            if conversation.exists():
                conversation.write({
                    'rating': str(rating),
                    'feedback': feedback
                })
                return {'success': True}
            return {'success': False, 'error': 'Conversation not found'}
        except Exception as e:
            _logger.error(f"Rating error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_or_create_conversation(self, session_id, partner_id, request_data):
        """Get existing conversation or create new one"""
        Conversation = request.env['chatbot.conversation'].sudo()
        
        if not session_id:
            session_id = f"session_{datetime.now().timestamp()}"
        
        # Try to find existing active conversation
        conversation = Conversation.search([
            ('session_id', '=', session_id),
            ('state', '=', 'active')
        ], limit=1)
        
        if not conversation:
            # Create new conversation
            vals = {
                'session_id': session_id,
                'user_ip': request_data.get('user_ip'),
                'user_agent': request_data.get('user_agent'),
            }
            if partner_id:
                vals['partner_id'] = partner_id
            
            conversation = Conversation.create(vals)
        
        return conversation
    
    def _get_bot_response(self, user_message, conversation):
        """
        Get bot response using RAG pipeline
        
        This method will:
        1. Call RAG service to retrieve relevant documents
        2. Call Gemini API to generate response
        3. Return response and metadata
        """
        import time
        start_time = time.time()
        
        try:
            # Get config
            config = request.env['chatbot.config'].sudo().get_active_config()
            
            # Step 1: Retrieve relevant documents from knowledge base
            retrieved_docs = self._retrieve_documents(user_message, config)
            
            # Step 2: Build context from retrieved documents
            context = self._build_context(retrieved_docs)
            
            # Step 3: Generate response using Gemini
            response = self._generate_response(user_message, context, config, conversation)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update usage count for retrieved docs
            for doc in retrieved_docs:
                doc.increment_usage()
            
            metadata = {
                'retrieved_docs': [doc.id for doc in retrieved_docs],
                'confidence_score': 0.8,  # TODO: Calculate actual confidence
                'model_used': config.groq_model,
                'response_time': response_time,
            }
            
            return response, metadata
            
        except Exception as e:
            _logger.error(f"RAG error: {str(e)}", exc_info=True)
            # Return fallback message
            config = request.env['chatbot.config'].sudo().get_active_config()
            return config.fallback_message, {'error': str(e)}
    
    def _retrieve_documents(self, query, config):
        """
        Retrieve relevant documents from knowledge base
        
        Improved keyword search - searches each word separately then combines results
        TODO: Implement vector similarity search with embeddings
        """
        KnowledgeBase = request.env['chatbot.knowledge.base'].sudo()
        
        _logger.info(f"RAG Search: query='{query}'")
        
        # Strategy 1: Try full query first
        docs = KnowledgeBase.search([
            ('active', '=', True),
            '|', '|',
            ('name', 'ilike', query),
            ('content_plain', 'ilike', query),
            ('keywords', 'ilike', query)
        ], limit=config.top_k_results, order='priority desc, usage_count desc')
        
        _logger.info(f"RAG Search: Full query found {len(docs)} docs")
        
        # Strategy 2: If no results, try individual words
        if not docs:
            query_words = [w for w in query.lower().split() if len(w) >= 2]
            _logger.info(f"RAG Search: Trying words: {query_words}")
            
            doc_ids = set()
            for word in query_words:
                word_docs = KnowledgeBase.search([
                    ('active', '=', True),
                    '|', '|',
                    ('name', 'ilike', word),
                    ('content_plain', 'ilike', word),
                    ('keywords', 'ilike', word)
                ])
                doc_ids.update(word_docs.ids)
                _logger.info(f"RAG Search: Word '{word}' found {len(word_docs)} docs")
            
            if doc_ids:
                docs = KnowledgeBase.browse(list(doc_ids))
                # Sort by priority
                docs = docs.sorted(key=lambda d: (d.priority, d.usage_count), reverse=True)
                docs = docs[:config.top_k_results]
        
        _logger.info(f"RAG Search: Final result: {len(docs)} documents")
        for doc in docs:
            _logger.info(f"  - {doc.name} (priority={doc.priority})")
        
        return docs
    
    def _build_context(self, documents):
        """Build context string from retrieved documents"""
        if not documents:
            return "Không có thông tin liên quan trong knowledge base."
        
        context_parts = []
        total_chars = 0
        max_context_chars = 8000  # Limit context to ~2000 tokens
        
        for i, doc in enumerate(documents, 1):
            # Get content, truncate if too long
            content = doc.content_plain or ""
            
            # Add document with clear formatting
            doc_text = f"""
=== TÀI LIỆU {i}: {doc.name} ===
{content}
===================================
"""
            
            # Check if adding this doc would exceed limit
            if total_chars + len(doc_text) > max_context_chars:
                # Truncate this document
                remaining = max_context_chars - total_chars
                if remaining > 200:  # Only add if we have meaningful space
                    truncated = content[:remaining] + "...[đã cắt bớt]"
                    doc_text = f"""
=== TÀI LIỆU {i}: {doc.name} ===
{truncated}
===================================
"""
                    context_parts.append(doc_text)
                break
            
            context_parts.append(doc_text)
            total_chars += len(doc_text)
        
        _logger.info(f"Built context with {len(context_parts)} documents, {total_chars} chars")
        return "\n".join(context_parts)
    
    def _generate_response(self, user_message, context, config, conversation):
        """
        Generate response using Gemini API
        """
        try:
            # Build conversation history
            history = self._get_conversation_history(conversation, limit=5)
            
            # Build prompt
            prompt = self._build_prompt(user_message, context, history, config)
            
            # Call Groq API
            response = self._call_groq_api(prompt, config)
            
            return response
            
        except Exception as e:
            _logger.error(f"Groq API error: {str(e)}")
            return config.fallback_message
    
    def _get_conversation_history(self, conversation, limit=5):
        """Get recent conversation history"""
        messages = request.env['chatbot.message'].sudo().search([
            ('conversation_id', '=', conversation.id)
        ], order='create_date desc', limit=limit * 2)
        
        history = []
        for msg in reversed(messages):
            role = 'user' if msg.message_type == 'user' else 'model'
            history.append({
                'role': role,
                'parts': [msg.content]
            })
        
        return history
    
    def _build_prompt(self, user_message, context, history, config):
        """Build the full prompt for Gemini"""
        system_prompt = config.system_prompt
        
        prompt = f"""{system_prompt}

THÔNG TIN TỪ KNOWLEDGE BASE:
{context}

---

HƯỚNG DẪN TRẢ LỜI:
1. ĐỌC KỸ nội dung trong các tài liệu trên
2. TÌM KIẾM thông tin liên quan đến câu hỏi của khách hàng
3. TỔNG HỢP và trả lời dựa trên nội dung tìm được
4. TRÍCH DẪN thông tin cụ thể từ tài liệu (không chỉ nói "theo tài liệu")
5. Nếu KHÔNG TÌM THẤY thông tin phù hợp, hãy thừa nhận và đề xuất liên hệ nhân viên

LƯU Ý:
- Trả lời bằng tiếng Việt, ngắn gọn nhưng đầy đủ
- Dựa vào NỘI DUNG tài liệu, không phải chỉ tiêu đề
- Nếu có nhiều thông tin liên quan, hãy tổng hợp lại
- Không bịa đặt thông tin không có trong tài liệu

Câu hỏi của khách hàng: {user_message}
"""
        return prompt
    
    def _call_groq_api(self, prompt, config):
        """
        Call Groq API to generate response (OpenAI-compatible format)
        """
        api_key = config.groq_api_key
        model = config.groq_model
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract text from response (OpenAI format)
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        
        raise Exception("Invalid response from Groq API")
