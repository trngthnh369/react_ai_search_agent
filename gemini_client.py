import google.generativeai as genai
import json
import logging
from typing import Dict, Any, List, Optional
from config import GEMINI_API_KEY, TEMPERATURE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        """
        Khởi tạo Gemini client
        """
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Tool definitions for function calling
        self.tools = [
            {
                "name": "search_action",
                "description": "Tìm kiếm thông tin trên Google sử dụng SerpAPI",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Từ khóa tìm kiếm"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Số lượng kết quả tìm kiếm (mặc định: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "extract_weather_data",
                "description": "Trích xuất dữ liệu thời tiết cho một địa điểm",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Tên địa điểm cần xem thời tiết"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "do_nothing",
                "description": "Không thực hiện hành động nào",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "summarize_action",
                "description": "Tóm tắt văn bản sử dụng thuật toán đơn giản",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Văn bản cần tóm tắt"
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "Độ dài tối đa của tóm tắt",
                            "default": 150
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "answer_question",
                "description": "Trả lời câu hỏi dựa trên kết quả tìm kiếm",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Câu hỏi cần trả lời"
                        },
                        "search_results": {
                            "type": "array",
                            "description": "Kết quả tìm kiếm",
                            "items": {
                                "type": "object"
                            }
                        },
                        "current_date": {
                            "type": "string",
                            "description": "Ngày hiện tại"
                        }
                    },
                    "required": ["question", "search_results", "current_date"]
                }
            }
        ]
    
    def generate_reasoning(self, context: str) -> Dict[str, Any]:
        """
        Tạo reasoning step cho ReAct Agent
        """
        try:
            prompt = f"""Bạn là một AI Search Agent sử dụng ReAct (Reasoning + Acting) framework.

Ngữ cảnh hiện tại:
{context}

Hãy phân tích tình huống và quyết định bước tiếp theo:

1. THOUGHT: Suy nghĩ về việc cần làm gì tiếp theo
2. ACTION: Quyết định action nào cần thực hiện (nếu có)
   - search_action: tìm kiếm thông tin
   - extract_weather_data: lấy thông tin thời tiết
   - summarize_action: tóm tắt văn bản
   - answer_question: trả lời câu hỏi cuối cùng
   - do_nothing: không làm gì cả

Trả lời theo format JSON:
{{
    "thought": "suy nghĩ của bạn về tình huống hiện tại",
    "action": {{
        "name": "tên_action",
        "parameters": {{
            "param1": "value1",
            "param2": "value2"
        }}
    }},
    "should_continue": true/false,
    "final_answer": "câu trả lời cuối cùng (nếu should_continue = false)"
}}

Lưu ý: 
- Nếu đã có đủ thông tin để trả lời, hãy set should_continue = false và đưa ra final_answer
- Nếu cần thêm thông tin, hãy chọn action phù hợp và set should_continue = true
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=TEMPERATURE,
                    max_output_tokens=1024,
                )
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            try:
                result = json.loads(response_text)
                return {
                    "success": True,
                    "result": result
                }
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Response text: {response_text}")
                
                # Fallback parsing
                return {
                    "success": False,
                    "error": f"Failed to parse JSON: {e}",
                    "raw_response": response_text
                }
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_final_response(self, user_input: str, history: List[Dict], final_answer: str) -> str:
        """
        Tạo phản hồi cuối cùng cho người dùng
        """
        try:
            # Create a summary of the reasoning process
            history_summary = ""
            for step in history[-6:]:  # Last 6 steps
                if step["type"] in ["thought", "observation"]:
                    history_summary += f"- {step['content'][:100]}...\n"
            
            prompt = f"""Dựa trên quá trình tìm kiếm và phân tích sau:

Câu hỏi của người dùng: {user_input}

Quá trình suy luận:
{history_summary}

Câu trả lời tìm được: {final_answer}

Hãy tạo một phản hồi cuối cùng ngắn gọn, rõ ràng và hữu ích cho người dùng. 
Phản hồi nên:
1. Trả lời trực tiếp câu hỏi
2. Cung cấp thông tin quan trọng nhất
3. Sử dụng tiếng Việt tự nhiên
4. Không quá dài dòng
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=512,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Final response generation error: {e}")
            return final_answer  # Fallback to original answer