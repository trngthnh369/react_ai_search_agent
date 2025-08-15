import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from agent_state import AgentState
from gemini_client import GeminiClient
from tools import (
    search_action, 
    extract_weather_data, 
    do_nothing, 
    summarize_action, 
    summarize_using_open_source_model,
    answer_question, 
    get_current_date
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReActAgent:
    def __init__(self):
        """
        Khởi tạo ReAct Agent
        """
        self.gemini_client = GeminiClient()
        self.function_mapping = {
            "search_action": search_action,
            "extract_weather_data": extract_weather_data,
            "do_nothing": do_nothing,
            "summarize_action": summarize_action,
            "answer_question": answer_question,
        }
        
    def reasoning_step(self, state: AgentState, user_input: str, intermediate_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực hiện bước suy luận của ReAct Agent
        """
        try:
            # Update state
            state.user_input = user_input
            state.intermediate_results = intermediate_results
            state.status = "thinking"
            
            # Get conversation context
            context = state.get_conversation_context()
            
            # Add intermediate results to context if available
            if intermediate_results:
                context += f"\nIntermediate Results:\n{json.dumps(intermediate_results, indent=2, ensure_ascii=False)}\n"
            
            # Generate reasoning using Gemini
            reasoning_result = self.gemini_client.generate_reasoning(context)
            
            if not reasoning_result["success"]:
                return {
                    "success": False,
                    "error": reasoning_result["error"],
                    "thought": "Không thể tạo suy luận",
                    "action": None,
                    "should_continue": False
                }
            
            result = reasoning_result["result"]
            
            # Extract components
            thought = result.get("thought", "Đang suy nghĩ...")
            action = result.get("action", None)
            should_continue = result.get("should_continue", True)
            final_answer = result.get("final_answer", "")
            
            # Update state
            state.current_thought = thought
            state.add_to_history("thought", thought)
            
            return {
                "success": True,
                "thought": thought,
                "action": action,
                "should_continue": should_continue,
                "final_answer": final_answer
            }
            
        except Exception as e:
            logger.error(f"Reasoning step error: {e}")
            state.status = "error"
            state.error = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "thought": "Đã xảy ra lỗi trong quá trình suy luận",
                "action": None,
                "should_continue": False
            }
    
    def process_tool_calls(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý các tool calls từ response
        """
        try:
            if not response.get("action"):
                return {
                    "success": True,
                    "result": "No action to perform",
                    "action_taken": "none"
                }
            
            action = response["action"]
            action_name = action.get("name", "")
            action_params = action.get("parameters", {})
            
            if action_name not in self.function_mapping:
                return {
                    "success": False,
                    "error": f"Unknown action: {action_name}",
                    "action_taken": action_name
                }
            
            # Execute the function
            logger.info(f"Executing action: {action_name} with params: {action_params}")
            function = self.function_mapping[action_name]
            result = function(**action_params)
            
            return {
                "success": True,
                "result": result,
                "action_taken": action_name,
                "action_params": action_params
            }
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "action_taken": action.get("name", "unknown") if "action" in locals() else "unknown"
            }
    
    def _advanced(self, state: AgentState, user_input: str, intermediate_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý nâng cao cho agent
        """
        try:
            # Kiểm tra xem có cần xử lý đặc biệt không
            user_input_lower = user_input.lower()
            
            # Xử lý các trường hợp đặc biệt
            if any(keyword in user_input_lower for keyword in ["tóm tắt", "tổng hợp", "summary"]):
                # Ưu tiên sử dụng model open source cho summarization
                if "text" in intermediate_results:
                    summary_result = summarize_using_open_source_model(
                        intermediate_results["text"], 
                        max_length=200
                    )
                    return {
                        "success": True,
                        "type": "advanced_summary",
                        "result": summary_result
                    }
            
            # Xử lý thời tiết
            if any(keyword in user_input_lower for keyword in ["thời tiết", "weather", "nhiệt độ"]):
                # Extract location from user input
                import re
                location_patterns = [
                    r"thời tiết (?:ở |tại |của )?([^?,.]+)",
                    r"weather (?:in |at |of )?([^?,.]+)",
                    r"nhiệt độ (?:ở |tại |của )?([^?,.]+)"
                ]
                
                location = None
                for pattern in location_patterns:
                    match = re.search(pattern, user_input_lower)
                    if match:
                        location = match.group(1).strip()
                        break
                
                if location:
                    weather_result = extract_weather_data(location)
                    return {
                        "success": True,
                        "type": "weather_extraction",
                        "result": weather_result
                    }
            
            # Xử lý tìm kiếm thông tin cụ thể
            if any(keyword in user_input_lower for keyword in ["tìm kiếm", "search", "tìm hiểu"]):
                # Thực hiện tìm kiếm với số lượng kết quả nhiều hơn
                search_result = search_action(user_input, num_results=15)
                return {
                    "success": True,
                    "type": "enhanced_search",
                    "result": search_result
                }
            
            return {
                "success": True,
                "type": "no_advanced_processing",
                "result": "No advanced processing needed"
            }
            
        except Exception as e:
            logger.error(f"Advanced processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "type": "error"
            }
    
    def react_agent(self, user_input: str) -> Dict[str, Any]:
        """
        Main ReAct Agent function - thực hiện vòng lặp ReAct
        """
        # Initialize state
        state = AgentState()
        state.user_input = user_input
        state.status = "started"
        
        logger.info(f"Starting ReAct Agent for input: {user_input}")
        
        try:
            while not state.finished and not state.is_max_iterations_reached():
                state.iteration += 1
                logger.info(f"=== Iteration {state.iteration} ===")
                
                # Step 1: Reasoning
                logger.info("Step 1: Reasoning...")
                reasoning_result = self.reasoning_step(state, user_input, state.intermediate_results)
                
                if not reasoning_result["success"]:
                    state.status = "error"
                    state.error = reasoning_result["error"]
                    break
                
                # Log thought
                logger.info(f"Thought: {reasoning_result['thought']}")
                
                # Check if we should finish
                if not reasoning_result["should_continue"]:
                    state.final_answer = reasoning_result["final_answer"]
                    state.finished = True
                    state.status = "finished"
                    break
                
                # Step 2: Action (if needed)
                if reasoning_result["action"]:
                    logger.info("Step 2: Taking action...")
                    state.status = "acting"
                    state.current_action = reasoning_result["action"]
                    
                    # Add action to history
                    action_description = f"Action: {reasoning_result['action']['name']} with params: {reasoning_result['action']['parameters']}"
                    state.add_to_history("action", action_description, {"action": reasoning_result["action"]})
                    logger.info(f"Action: {action_description}")
                    
                    # Execute action
                    action_result = self.process_tool_calls(reasoning_result)
                    
                    if action_result["success"]:
                        # Store results for next iteration
                        tool_result = action_result["result"]
                        state.intermediate_results[f"action_{state.iteration}"] = tool_result
                        
                        # Step 3: Observation
                        logger.info("Step 3: Observation...")
                        state.status = "observing"
                        
                        if isinstance(tool_result, dict):
                            if tool_result.get("success", True):
                                observation = f"Action executed successfully. Result: {json.dumps(tool_result, ensure_ascii=False, indent=2)[:300]}..."
                            else:
                                observation = f"Action failed: {tool_result.get('error', 'Unknown error')}"
                        else:
                            observation = f"Action result: {str(tool_result)[:300]}..."
                        
                        state.current_observation = observation
                        state.add_to_history("observation", observation)
                        logger.info(f"Observation: {observation[:200]}...")
                        
                        # Check if we have enough information to answer
                        if reasoning_result["action"]["name"] == "answer_question":
                            if tool_result.get("success", False):
                                state.final_answer = tool_result.get("answer", "Không thể tạo câu trả lời.")
                                state.finished = True
                                state.status = "finished"
                            else:
                                state.final_answer = "Không thể tìm thấy thông tin để trả lời câu hỏi."
                                state.finished = True
                                state.status = "finished"
                    else:
                        # Action failed
                        observation = f"Action failed: {action_result['error']}"
                        state.current_observation = observation
                        state.add_to_history("observation", observation)
                        logger.error(f"Action failed: {action_result['error']}")
                
                # Advanced processing if needed
                advanced_result = self._advanced(state, user_input, state.intermediate_results)
                if advanced_result["success"] and advanced_result["type"] != "no_advanced_processing":
                    state.intermediate_results["advanced"] = advanced_result["result"]
            
            # Handle max iterations reached
            if state.is_max_iterations_reached() and not state.finished:
                state.status = "max_iterations_reached"
                state.final_answer = "Đã đạt tới số lần thử tối đa. Không thể hoàn thành yêu cầu."
                state.finished = True
            
            # Generate final response using Gemini
            if state.final_answer and state.status == "finished":
                try:
                    enhanced_response = self.gemini_client.generate_final_response(
                        user_input, 
                        state.history, 
                        state.final_answer
                    )
                    if enhanced_response:
                        state.final_answer = enhanced_response
                except Exception as e:
                    logger.error(f"Final response enhancement failed: {e}")
            
            # Return results
            result = {
                "success": True,
                "user_input": user_input,
                "final_answer": state.final_answer,
                "total_iterations": state.iteration,
                "execution_time": state.get_execution_time(),
                "status": state.status,
                "history": state.history,
                "intermediate_results": state.intermediate_results,
                "summary": state.get_summary()
            }
            
            logger.info(f"ReAct Agent completed in {state.iteration} iterations")
            logger.info(f"Final answer: {state.final_answer[:200]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"ReAct Agent error: {e}")
            state.status = "error"
            state.error = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "user_input": user_input,
                "total_iterations": state.iteration,
                "execution_time": state.get_execution_time(),
                "status": state.status,
                "history": state.history,
                "summary": state.get_summary()
            }