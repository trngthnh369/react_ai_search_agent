# ReAct AI Search Agent

Một hệ thống AI Search Agent thông minh sử dụng ReAct (Reasoning + Acting) framework với Gemini 2.0, tích hợp nhiều công cụ mạnh mẽ để tìm kiếm và phân tích thông tin.

## 🚀 Tính năng chính

### Core Features
- **ReAct Framework**: Suy luận và hành động liên tục để giải quyết vấn đề
- **Gemini 2.0 Integration**: Sử dụng AI model mạnh mẽ nhất của Google
- **Multi-tool Support**: Tích hợp nhiều công cụ chuyên dụng
- **Vietnamese Language Support**: Tối ưu cho tiếng Việt

### Available Tools
1. **search_action**: Tìm kiếm thông tin trên Google (SerpAPI)
2. **extract_weather_data**: Trích xuất dữ liệu thời tiết
3. **summarize_action**: Tóm tắt văn bản (thuật toán đơn giản)
4. **summarize_using_open_source_model**: Tóm tắt với T5 Vietnamese
5. **answer_question**: Trả lời câu hỏi dựa trên kết quả tìm kiếm
6. **do_nothing**: Không thực hiện hành động

## 📋 Yêu cầu hệ thống

- Python 3.8+
- RAM: 4GB+ (khuyến nghị 8GB để chạy model T5)
- Internet connection để sử dụng APIs

## 🛠️ Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/trngthnh369/react_ai_search_agent.git
cd react-ai-search-agent
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
cp .env.example .env
```

Chỉnh sửa file `.env` và thêm API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here
SUMMARIZATION_MODEL=minhtoan/t5-small-wikilingua_vietnamese
```

## 🔑 Lấy API Keys

### Gemini API Key
1. Truy cập [Google AI Studio](https://makersuite.google.com/)
2. Đăng nhập với Google account
3. Tạo API key mới
4. Copy key vào file `.env`

### SerpAPI Key
1. Truy cập [SerpAPI](https://serpapi.com/)
2. Đăng ký tài khoản miễn phí
3. Lấy API key từ dashboard
4. Copy key vào file `.env`

## 🎯 Cách sử dụng

### Interactive Mode (Khuyến nghị)
```bash
python main.py interactive
# hoặc
python main.py i
```

### Single Query Mode
```bash
python main.py query "Thời tiết Hà Nội hôm nay như thế nào?"
```

### Test Mode
```bash
python main.py test
```

### Direct Python Usage
```python
from react_agent import ReActAgent

# Khởi tạo agent
agent = ReActAgent()

# Chạy query
result = agent.react_agent("Giá Bitcoin hiện tại là bao nhiều?")

# Xem kết quả
print(result["final_answer"])
```

## 📖 Ví dụ sử dụng

### Tìm kiếm thông tin
```
User: "Tìm hiểu về ChatGPT-4 mới nhất"
Agent: Tìm kiếm thông tin... → Phân tích kết quả → Trả lời chi tiết
```

### Thời tiết
```
User: "Thời tiết TP.HCM hôm nay?"
Agent: Trích xuất dữ liệu thời tiết → Tổng hợp thông tin → Báo cáo thời tiết
```

### Tóm tắt thông tin
```
User: "Tóm tắt tin tức công nghệ hôm nay"
Agent: Tìm kiếm tin tức → Sử dụng model T5 → Tạo tóm tắt
```

## 🏗️ Kiến trúc hệ thống

```
├── main.py                 # Entry point
├── react_agent.py          # Core ReAct Agent logic
├── gemini_client.py        # Gemini API integration
├── tools.py                # All available tools
├── agent_state.py          # Agent state management
├── config.py               # Configuration management
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── README.md              # Documentation
```

### Agent Workflow
1. **User Input** → **Reasoning** (Gemini 2.0)
2. **Action Selection** → **Tool Execution**
3. **Observation** → **State Update**
4. **Continue/Finish Decision**
5. **Final Response Generation**

## ⚙️ Configuration

### Agent Settings
```python
# config.py
MAX_ITERATIONS = 10      # Số vòng lặp tối đa
TEMPERATURE = 0.7        # Độ creativity của model
```

### Tool Mapping
```python
# react_agent.py
function_mapping = {
    "search_action": search_action,
    "extract_weather_data": extract_weather_data,
    "do_nothing": do_nothing,
    "summarize_action": summarize_action,
    "answer_question": answer_question,
}
```

## 📊 Monitoring & Logging

### Log Files
- `agent.log`: Chi tiết quá trình thực thi
- `agent_result_*.json`: Kết quả chi tiết từng query

### Metrics Tracking
- Execution time
- Number of iterations
- Tools used
- Success/failure rates

## 🔧 Customization

### Thêm Tool mới
1. Tạo function trong `tools.py`:
```python
def new_tool(param1: str) -> Dict[str, Any]:
    # Implementation
    return {"success": True, "result": "..."}
```

2. Thêm vào mapping:
```python
function_mapping["new_tool"] = new_tool
```

3. Update Gemini client với tool definition

### Tùy chỉnh Prompts
Chỉnh sửa prompts trong `gemini_client.py` để phù hợp với use case cụ thể.

## 🐛 Troubleshooting

### Common Issues

**1. API Key errors**
```
ValueError: GEMINI_API_KEY environment variable is required
```
→ Check `.env` file và đảm bảo API keys được set đúng

**2. Model loading errors**
```
Failed to load summarization model
```
→ Đảm bảo có đủ RAM và internet connection

**3. SerpAPI quota exceeded**
```
SerpAPI monthly quota exceeded
```
→ Check usage tại SerpAPI dashboard

### Debug Mode
```bash
export PYTHONPATH=.
python -m logging.basicConfig level=DEBUG
python main.py interactive
```

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 📞 Support

- 🐛 **Bug Reports**: Tạo issue trên GitHub
- 💡 **Feature Requests**: Tạo issue với label "enhancement"
- 📧 **Email**: truongthinhnguyen30303@gmail.com

## 🙏 Acknowledgments

- Google Gemini 2.0 API
- SerpAPI for search functionality
- Hugging Face Transformers
- minhtoan/t5-small-wikilingua_vietnamese model
