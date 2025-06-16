# 🎮 LangChain Tools Playground

**Learn and explore LangChain's pre-built tools through hands-on demonstrations.**

This interactive Streamlit application is designed to teach developers how to use LangChain's built-in tools for information retrieval without the complexity of LLM integration.

## 🎯 What You'll Learn

### **LangChain Tools Made Simple**
- **Direct Tool Integration**: See how LangChain tools work without LLM overhead
- **Structured Outputs**: Experience consistent JSON formatting across different tools
- **Error Handling**: Learn proper tool error management and validation
- **UI Enhancement**: Discover how to create rich interfaces for tool outputs

### **Featured Tools**
1. **📚 Wikipedia Tool** - Access encyclopedic content with enhanced formatting
2. **🎥 YouTube Tool** - Search and preview videos with embedded players  
3. **🔍 Tavily Tool** - Web search with AI summaries and relevance scoring

## ✨ Key Features

### **Smart Input Validation**
- Real-time typo detection and suggestions
- Fuzzy matching with common search terms
- Tool-specific example suggestions
- Intelligent error messages

### **Enhanced UI Components**
- **YouTube**: Embedded video previews and action buttons
- **Wikipedia**: Structured article display with image support
- **Tavily**: Card-based results with star ratings and AI summaries

### **Developer-Friendly**
- **No LLM API keys required** for basic functionality
- **Fast responses** - direct API access without model inference
- **Cost-effective** - no token usage for search operations
- **Educational** - clear code structure for learning

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd langchain-tools-playground
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   
   Copy the `.env` file and add your API keys:
   ```bash
   cp .env .env.local
   ```
   
   Edit `.env.local` and add your API keys:
   ```bash
   # Required for Tavily web search
   TAVILY_API_KEY=your_tavily_api_key_here
   
   # Optional for enhanced YouTube functionality
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   
   Open your browser and navigate to `http://localhost:8501`

## 🔑 API Keys Setup

### Tavily API Key (Required for Web Search)
1. Visit [Tavily.com](https://tavily.com/)
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key
5. Add it to your `.env` file

### YouTube API Key (Optional)
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add it to your `.env` file

## 🛠️ Usage

1. **Enter Search Query**: Type your question or search term in the text area
2. **Select Tool**: Choose from Wikipedia, YouTube, or Tavily based on your needs
3. **Execute Search**: Click the "Execute Search" button
4. **View Results**: See both structured JSON response and readable content
5. **Reset**: Use the reset button to clear your input

### Tool Selection Guide

- **Wikipedia**: Best for encyclopedic information, definitions, historical facts
- **YouTube**: Perfect for finding video content, tutorials, entertainment
- **Tavily**: Ideal for current events, recent information, comprehensive web search

## 📁 Project Structure

```
langchain-tools-playground/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables template
├── .env.local                     # Local environment variables
├── .gitignore                     # Git ignore rules
├── README.md                      # Project documentation
├── venv/                          # Virtual environment
└── notebooks/                     # Jupyter notebooks
    └── tools.ipynb                # Tool exploration notebook
```

## 🔧 Technical Details

### Dependencies

- **streamlit**: Web application framework
- **langchain**: LLM application development framework
- **langchain-community**: Community tools and utilities
- **python-dotenv**: Environment variable management
- **wikipedia**: Wikipedia API wrapper
- **youtube-search-python**: YouTube search functionality
- **tavily-python**: Tavily search engine integration

### Architecture

The application follows a modular architecture:

1. **Tool Initialization**: Sets up LangChain tools with proper configuration
2. **Query Processing**: Handles user input and tool selection
3. **Response Formatting**: Structures tool outputs into consistent JSON format
4. **UI Components**: Streamlit interface with intuitive controls

## 🔧 LangChain Tools Integration

### **Why LangChain Tools?**

LangChain's pre-built tools provide several advantages for developers:

#### **🚀 Easy Integration**
```python
# Simple tool initialization
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
result = wikipedia.invoke("artificial intelligence")
```

#### **📊 Consistent Interface**
- All tools follow the same `.invoke(query)` pattern
- Standardized error handling across different services
- Uniform response structures for easy processing

#### **🔒 Built-in Safety**
- Input validation and sanitization
- Rate limiting and error management
- Secure API key handling

#### **⚡ Performance Benefits**
- **No LLM calls** - Direct API access for faster responses
- **Lower costs** - Avoid token usage for simple searches
- **Better reliability** - Fewer points of failure

### **Tool-Specific Features**

#### **Wikipedia Tool**
```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Rich content retrieval
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
result = wikipedia.invoke("machine learning")
# Returns: Comprehensive article content with references
```

#### **YouTube Tool**
```python
from langchain_community.tools import YouTubeSearchTool

# Video search and metadata
youtube = YouTubeSearchTool()
result = youtube.invoke("python tutorial")
# Returns: List of video URLs with titles and descriptions
```

#### **Tavily Tool**
```python
from langchain_tavily import TavilySearch

# Advanced web search with AI summaries
tavily = TavilySearch(api_key="your_api_key")
result = tavily.invoke("latest AI news")
# Returns: Structured results with relevance scores and summaries
```

## 💡 Learning Outcomes

After using this application, you'll understand:

### **Technical Skills**
- How to integrate LangChain tools into web applications
- Proper error handling and validation patterns
- UI/UX design for tool-based applications
- Session state management in Streamlit

### **Best Practices**
- Input validation and user feedback
- Structured output formatting
- Progressive enhancement techniques
- Accessibility considerations

### **LangChain Concepts**
- Tool ecosystem and available integrations
- Direct tool usage vs. LLM-mediated tool calling
- Performance optimization strategies
- Cost-effective application architecture

## 🌟 Benefits

- **No LLM Calls**: Direct tool integration without language model overhead
- **Fast Responses**: Immediate results from native API calls
- **Structured Output**: Consistent JSON formatting for all responses
- **Cost-Effective**: No token usage for search operations
- **Secure**: API keys managed through environment variables
- **Educational**: Learn LangChain tools through hands-on practice

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🚧 Future Enhancements

- Add more LangChain tools (DuckDuckGo, Bing, etc.)
- Implement search history
- Add export functionality for results
- Create user authentication
- Add rate limiting and caching
- Implement batch search capabilities

---

**Suggested Branch Name**: `feature/langchain-tools-streamlit-hub`

Built with ❤️ using Streamlit and LangChain