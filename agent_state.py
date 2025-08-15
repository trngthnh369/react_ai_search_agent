from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class AgentState:
    """
    Trạng thái của ReAct Agent
    """
    # Current iteration
    iteration: int = 0
    
    # Maximum iterations allowed
    max_iterations: int = 10
    
    # Current user input
    user_input: str = ""
    
    # History of thoughts, actions, and observations
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Current thought process
    current_thought: str = ""
    
    # Current action to take
    current_action: Optional[Dict[str, Any]] = None
    
    # Current observation from last action
    current_observation: str = ""
    
    # Intermediate results from tools
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    
    # Final answer
    final_answer: str = ""
    
    # Whether the agent has finished
    finished: bool = False
    
    # Start time
    start_time: datetime = field(default_factory=datetime.now)
    
    # Current status
    status: str = "initialized"  # initialized, thinking, acting, observing, finished, error
    
    # Error information if any
    error: Optional[str] = None
    
    def add_to_history(self, step_type: str, content: str, metadata: Optional[Dict] = None):
        """
        Thêm một bước vào lịch sử
        """
        step = {
            "iteration": self.iteration,
            "type": step_type,  # "thought", "action", "observation"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.history.append(step)
    
    def get_conversation_context(self, max_steps: int = 6) -> str:
        """
        Lấy ngữ cảnh cuộc hội thoại gần đây
        """
        recent_history = self.history[-max_steps:] if len(self.history) > max_steps else self.history
        
        context = f"User Input: {self.user_input}\n\n"
        context += "Recent History:\n"
        
        for step in recent_history:
            context += f"[{step['type'].upper()}] {step['content']}\n"
        
        return context
    
    def is_max_iterations_reached(self) -> bool:
        """
        Kiểm tra xem đã đạt tới số iteration tối đa chưa
        """
        return self.iteration >= self.max_iterations
    
    def reset(self):
        """
        Reset trạng thái agent
        """
        self.iteration = 0
        self.history = []
        self.current_thought = ""
        self.current_action = None
        self.current_observation = ""
        self.intermediate_results = {}
        self.final_answer = ""
        self.finished = False
        self.start_time = datetime.now()
        self.status = "initialized"
        self.error = None
    
    def get_execution_time(self) -> float:
        """
        Lấy thời gian thực thi
        """
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Lấy tóm tắt về quá trình thực thi
        """
        return {
            "user_input": self.user_input,
            "total_iterations": self.iteration,
            "final_answer": self.final_answer,
            "execution_time": self.get_execution_time(),
            "status": self.status,
            "finished": self.finished,
            "error": self.error,
            "total_steps": len(self.history)
        }