import json
import requests
from datetime import datetime
from typing import Dict, Any, List
# from serpapi.google_search import GoogleSearch
import serpapi
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import logging
from config import SERPAPI_KEY, SUMMARIZATION_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Tools:
    def __init__(self):
        # Initialize summarization model
        try:
            self.summarization_tokenizer = T5Tokenizer.from_pretrained(SUMMARIZATION_MODEL)
            self.summarization_model = T5ForConditionalGeneration.from_pretrained(SUMMARIZATION_MODEL)
            logger.info(f"Loaded summarization model: {SUMMARIZATION_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            self.summarization_tokenizer = None
            self.summarization_model = None

def search_action(query: str, num_results: int = 10) -> Dict[str, Any]:
    """
    Tìm kiếm thông tin sử dụng SerpAPI Google Search
    """
    # try:
    #     search = GoogleSearch({
    #         "q": query,
    #         "api_key": SERPAPI_KEY,
    #         "num": num_results,
    #         "hl": "vi",
    #         "gl": "vn"
    #     })
    #     results = search.get_dict()
        
    #     # Extract relevant information
    #     search_results = []
    #     if "organic_results" in results:
    #         for result in results["organic_results"]:
    #             search_results.append({
    #                 "title": result.get("title", ""),
    #                 "link": result.get("link", ""),
    #                 "snippet": result.get("snippet", ""),
    #                 "position": result.get("position", 0)
    #             })
        
    #     return {
    #         "success": True,
    #         "query": query,
    #         "results": search_results,
    #         "total_results": len(search_results),
    #         "timestamp": datetime.now().isoformat()
    #     }
    # except Exception as e:
    #     logger.error(f"Search error: {e}")
    #     return {
    #         "success": False,
    #         "error": str(e),
    #         "query": query,
    #         "results": [],
    #         "total_results": 0,
    #         "timestamp": datetime.now().isoformat()
    #     }
    
    try:
        client = serpapi.Client(api_key=SERPAPI_KEY)
        results = client.search({
            "engine": "google",
            "q": query,
            "num": num_results,
            "hl": "vi",
            "gl": "vn"
        })

        search_results = []
        if "organic_results" in results:
            for result in results["organic_results"]:
                search_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                })

        return {
            "success": True,
            "query": query,
            "results": search_results,
            "total_results": len(search_results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": [],
            "total_results": 0,
            "timestamp": datetime.now().isoformat()
        }

def extract_weather_data(location: str) -> Dict[str, Any]:
    """
    Trích xuất dữ liệu thời tiết cho một địa điểm cụ thể
    """
    try:
        # Search for weather information
        weather_query = f"thời tiết {location} hôm nay"
        search_result = search_action(weather_query, num_results=3)
        
        if not search_result["success"]:
            return {
                "success": False,
                "error": "Failed to search weather data",
                "location": location
            }
        
        # Extract weather info from search results
        weather_info = []
        for result in search_result["results"]:
            if any(keyword in result["snippet"].lower() for keyword in ["°c", "nhiệt độ", "thời tiết", "độ c"]):
                weather_info.append({
                    "source": result["title"],
                    "information": result["snippet"],
                    "link": result["link"]
                })
        
        return {
            "success": True,
            "location": location,
            "weather_data": weather_info,
            "search_query": weather_query,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Weather extraction error: {e}")
        return {
            "success": False,
            "error": str(e),
            "location": location,
            "weather_data": [],
            "timestamp": datetime.now().isoformat()
        }

def do_nothing() -> Dict[str, Any]:
    """
    Hàm không làm gì cả, sử dụng khi không cần thực hiện action nào
    """
    return {
        "success": True,
        "action": "do_nothing",
        "message": "No action performed",
        "timestamp": datetime.now().isoformat()
    }

def summarize_action(text: str, max_length: int = 150) -> Dict[str, Any]:
    """
    Tóm tắt văn bản sử dụng các thuật toán đơn giản
    """
    try:
        if not text or len(text.strip()) == 0:
            return {
                "success": False,
                "error": "Empty text provided",
                "original_length": 0,
                "summary": "",
                "timestamp": datetime.now().isoformat()
            }
        
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Simple extractive summarization - take first few sentences
        if len(sentences) <= 3:
            summary = text
        else:
            # Take first 2 and last 1 sentence
            summary = '. '.join(sentences[:2] + sentences[-1:]) + '.'
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return {
            "success": True,
            "original_text": text[:200] + "..." if len(text) > 200 else text,
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / len(text), 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_text": text[:200] + "..." if len(text) > 200 else text,
            "summary": "",
            "timestamp": datetime.now().isoformat()
        }

def summarize_using_open_source_model(text: str, max_length: int = 150) -> Dict[str, Any]:
    """
    Tóm tắt văn bản sử dụng mô hình T5 Vietnamese
    """
    tools = Tools()
    
    try:
        if not tools.summarization_model or not tools.summarization_tokenizer:
            # Fallback to simple summarization
            logger.warning("Model not available, using simple summarization")
            return summarize_action(text, max_length)
        
        # Prepare input for T5 model
        input_text = f"summarize: {text}"
        
        # Tokenize
        inputs = tools.summarization_tokenizer.encode(
            input_text, 
            return_tensors="pt", 
            max_length=512, 
            truncation=True
        )
        
        # Generate summary
        with torch.no_grad():
            outputs = tools.summarization_model.generate(
                inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                temperature=0.7
            )
        
        # Decode the summary
        summary = tools.summarization_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "success": True,
            "model_used": SUMMARIZATION_MODEL,
            "original_text": text[:200] + "..." if len(text) > 200 else text,
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / len(text), 2) if len(text) > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Model summarization error: {e}")
        # Fallback to simple summarization
        return summarize_action(text, max_length)

def answer_question(question: str, search_results: List[Dict], current_date: str) -> Dict[str, Any]:
    """
    Trả lời câu hỏi dựa trên kết quả tìm kiếm
    """
    try:
        if not search_results:
            return {
                "success": False,
                "error": "No search results provided",
                "question": question,
                "answer": "Không tìm thấy thông tin liên quan đến câu hỏi của bạn.",
                "sources": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Combine relevant information from search results
        relevant_info = []
        sources = []
        
        for result in search_results[:5]:  # Use top 5 results
            if result.get("snippet"):
                relevant_info.append(result["snippet"])
                sources.append({
                    "title": result.get("title", "Unknown"),
                    "link": result.get("link", ""),
                    "snippet": result["snippet"][:100] + "..." if len(result["snippet"]) > 100 else result["snippet"]
                })
        
        # Create a comprehensive answer
        combined_info = " ".join(relevant_info)
        
        # Simple answer generation based on available information
        if len(combined_info.strip()) == 0:
            answer = "Không tìm thấy thông tin chi tiết để trả lời câu hỏi này."
        else:
            # Summarize the combined information
            summary_result = summarize_action(combined_info, max_length=300)
            if summary_result["success"]:
                answer = f"Dựa trên thông tin tìm kiếm được (cập nhật {current_date}): {summary_result['summary']}"
            else:
                answer = f"Dựa trên thông tin tìm kiếm được: {combined_info[:300]}..."
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "sources": sources,
            "total_sources": len(sources),
            "current_date": current_date,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Answer generation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "question": question,
            "answer": "Đã xảy ra lỗi khi tạo câu trả lời.",
            "sources": [],
            "timestamp": datetime.now().isoformat()
        }

def get_current_date() -> str:
    """
    Lấy ngày hiện tại
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")