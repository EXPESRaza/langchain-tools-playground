import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import YouTubeSearchTool
from langchain_tavily import TavilySearch
from langchain.schema import StrOutputParser
import json
import re
from urllib.parse import urlparse
import difflib

load_dotenv()

# Common search terms database for suggestions
COMMON_SEARCH_TERMS = [
    # Popular places
    "mount everest", "mount rainier", "mount fuji", "mount kilimanjaro", "mount mckinley", "mount shasta",
    "new york", "los angeles", "san francisco", "chicago", "miami", "seattle", "boston",
    "london", "paris", "tokyo", "berlin", "rome", "madrid", "moscow", "beijing",
    
    # Science & Technology
    "artificial intelligence", "machine learning", "deep learning", "neural networks",
    "climate change", "global warming", "renewable energy", "solar energy", "wind energy",
    "quantum physics", "quantum computing", "blockchain", "cryptocurrency", "bitcoin",
    "python programming", "javascript tutorial", "react tutorial", "nodejs tutorial",
    
    # History & Culture
    "world war ii", "american revolution", "ancient egypt", "roman empire", "medieval times",
    "renaissance period", "industrial revolution", "civil rights movement",
    
    # Entertainment
    "cooking recipes", "music videos", "movie reviews", "book recommendations",
    "travel destinations", "fitness tips", "health advice", "meditation techniques",
    
    # Current Topics
    "latest news", "weather forecast", "stock market", "sports scores", "election results",
    "vaccine information", "covid updates", "economic trends",
    
    # Educational
    "math tutorial", "science experiments", "history lessons", "language learning",
    "study tips", "career advice", "job interviews", "resume writing",
    
    # Popular YouTube searches
    "how to cook", "guitar lessons", "dance tutorial", "makeup tutorial", "workout videos",
    "tech reviews", "gaming videos", "comedy sketches", "documentary films",
    
    # Wikipedia popular topics
    "solar system", "human anatomy", "periodic table", "world geography", "famous people",
    "historical events", "scientific discoveries", "literary works", "art movements"
]

def get_search_suggestions(query, max_suggestions=3):
    """Get search suggestions using fuzzy matching"""
    if not query or len(query.strip()) < 3:
        return []
    
    query = query.lower().strip()
    
    # Use difflib to find close matches
    matches = difflib.get_close_matches(
        query, 
        COMMON_SEARCH_TERMS, 
        n=max_suggestions, 
        cutoff=0.4  # Lower cutoff for more flexible matching
    )
    
    # If no close matches, try partial matching
    if not matches:
        partial_matches = []
        for term in COMMON_SEARCH_TERMS:
            # Check if query is a substring or if term contains similar words
            if (query in term or 
                term in query or 
                any(word in term for word in query.split() if len(word) > 2)):
                partial_matches.append(term)
        
        # Sort by similarity and take top matches
        partial_matches = sorted(partial_matches, key=lambda x: difflib.SequenceMatcher(None, query, x).ratio(), reverse=True)
        matches = partial_matches[:max_suggestions]
    
    return matches

def initialize_tools():
    """Initialize the LangChain tools"""
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    youtube = YouTubeSearchTool()
    tavily = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))
    
    return {
        "Wikipedia": wikipedia,
        "YouTube": youtube,
        "Tavily": tavily
    }

def format_response(response, tool_name):
    """Format the tool response into a structured format"""
    try:
        if tool_name == "Wikipedia":
            return {
                "tool": "wikipedia",
                "content": response,
                "source": "Wikipedia API",
                "type": "encyclopedic_content"
            }
        elif tool_name == "YouTube":
            return {
                "tool": "youtube_search",
                "content": response,
                "source": "YouTube Search",
                "type": "video_search_results"
            }
        elif tool_name == "Tavily":
            return {
                "tool": "Tavily",
                "content": response,
                "source": "Tavily Search Engine",
                "type": "web_search_results"
            }
    except Exception as e:
        return {
            "tool": tool_name,
            "error": str(e),
            "content": "Error occurred while processing the response"
        }

def validate_search_input(query):
    """Validate search input and return validation result with suggestions"""
    if not query or not query.strip():
        return False, "❌ Please enter a search query", []
    
    query = query.strip()
    
    # Check minimum length
    if len(query) < 2:
        return False, "❌ Search query is too short (minimum 2 characters)", []
    
    # Check if it's just numbers or symbols
    if query.isdigit():
        suggestions = get_search_suggestions(query)
        return False, "⚠️ Please provide a more descriptive search query instead of just numbers", suggestions
    
    # Check for common invalid patterns
    invalid_patterns = [
        r'^[^\w\s]+$',  # Only special characters
        r'^(.)\1{4,}$',  # Repeated character (5+ times)
        r'^\s*$',       # Only whitespace
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, query):
            suggestions = get_search_suggestions(query)
            return False, "❌ Please enter a meaningful search query", suggestions
    
    # Check for very long queries (might be gibberish)
    if len(query) > 500:
        return False, "❌ Search query is too long (maximum 500 characters)", []
    
    # Check for excessive repetition of words
    words = query.lower().split()
    if len(words) > 3:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # If any word appears more than half the total words, it's likely spam
        for word, count in word_counts.items():
            if count > len(words) // 2:
                suggestions = get_search_suggestions(query)
                return False, f"⚠️ Too much repetition detected. Please provide a clearer search query", suggestions
    
    # Check for potential typos by looking for suggestions
    suggestions = get_search_suggestions(query)
    
    # If we found close matches that are significantly different, it might be a typo
    if suggestions:
        best_match = suggestions[0]
        similarity = difflib.SequenceMatcher(None, query.lower(), best_match).ratio()
        
        # Only suggest if similarity is between 0.6 and 0.9 AND the query is clearly different
        # This prevents valid searches like "mount shasta" from being flagged
        if 0.6 <= similarity < 0.9 and len(query) >= 5:
            # Check if it's likely a typo by looking for character differences
            query_words = set(query.lower().split())
            best_words = set(best_match.lower().split())
            
            # If words are very similar but not exact, might be a typo
            word_similarities = []
            for q_word in query_words:
                for b_word in best_words:
                    word_sim = difflib.SequenceMatcher(None, q_word, b_word).ratio()
                    word_similarities.append(word_sim)
            
            # Only flag as typo if we have high word similarity but not exact match
            if word_similarities and max(word_similarities) > 0.8:
                return False, f"⚠️ Did you mean something else? Your query '{query}' might have a typo", suggestions
    
    return True, "✅ Search query looks good!", []

def execute_tool(query, selected_tool, tools):
    """Execute the selected tool with the given query"""
    try:
        tool = tools[selected_tool]
        response = tool.invoke(query)
        return format_response(response, selected_tool)
    except Exception as e:
        return {
            "tool": selected_tool,
            "error": str(e),
            "content": f"Error executing {selected_tool} tool"
        }

def extract_youtube_links(text):
    """Extract YouTube video IDs from text"""
    youtube_pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)'
    matches = re.findall(youtube_pattern, str(text))
    return matches

def extract_image_urls(text):
    """Extract image URLs from text"""
    image_pattern = r'https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp|svg)'
    matches = re.findall(image_pattern, str(text), re.IGNORECASE)
    return matches

def display_enhanced_results(result):
    """Display results with enhanced formatting and media support"""
    if "error" in result:
        st.error(f"❌ Error with {result['tool']}: {result['error']}")
        return
    
    # Tool header with icon
    tool_icons = {
        "wikipedia": "📚", 
        "youtube_search": "🎥", 
        "YouTube": "🎥",
        "Tavily": "🔍"
    }
    
    tool_names = {
        "wikipedia": "Wikipedia",
        "youtube_search": "YouTube", 
        "YouTube": "YouTube",
        "Tavily": "Tavily"
    }
    
    icon = tool_icons.get(result['tool'], "🔧")
    display_name = tool_names.get(result['tool'], result['tool'])
    
    st.subheader(f"{icon} {display_name} Results")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📖 Formatted", "🎯 Summary", "🔧 Raw Data"])
    
    with tab1:
        content = result.get("content", "")
        
        if result['tool'] in ["YouTube", "youtube_search"]:
            display_youtube_results(content)
        elif result['tool'] in ["Wikipedia", "wikipedia"]:
            display_wikipedia_results(content)
        elif result['tool'] == "Tavily":
            display_tavily_results(content)
        else:
            st.markdown(str(content))
    
    with tab2:
        # Enhanced summary view
        st.info(f"**Source:** {result.get('source', 'Unknown')}")
        st.info(f"**Type:** {result.get('type', 'Unknown').replace('_', ' ').title()}")
        
        # Display key information
        content = str(result.get("content", ""))
        if len(content) > 500:
            st.markdown("**Summary:**")
            st.markdown(content[:500] + "...")
            with st.expander("📋 Show Full Content"):
                st.markdown(content)
        else:
            st.markdown("**Content:**")
            st.markdown(content)
    
    with tab3:
        # Raw JSON data in an expandable format
        st.json(result)

def display_youtube_results(content):
    """Enhanced display for YouTube search results with video previews"""
    try:
        st.markdown("### 🎥 Video Search Results")
        
        # The YouTube tool returns a string that looks like a Python list
        youtube_urls = []
        
        if isinstance(content, str):
            # Try to parse the string as a Python list using ast.literal_eval
            try:
                import ast
                parsed_content = ast.literal_eval(content)
                if isinstance(parsed_content, list):
                    youtube_urls = parsed_content
            except:
                # If parsing fails, extract URLs using regex
                youtube_urls = re.findall(r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+[^\s\'\"\]]*)', content)
        
        if youtube_urls:
            st.markdown(f"Found {len(youtube_urls)} video(s)")
            
            for i, url in enumerate(youtube_urls[:5]):  # Show up to 5 videos
                with st.container():
                    st.markdown(f"#### 🎬 Video {i+1}")
                    
                    # Create columns for video and controls
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        try:
                            # Clean URL (remove extra parameters that might cause issues)
                            clean_url = url.split('&')[0] if '&' in url else url
                            st.video(clean_url)
                        except Exception as e:
                            st.error(f"Could not embed video: {str(e)}")
                            st.markdown(f"🔗 [Watch Video on YouTube]({url})")
                    
                    with col2:
                        st.markdown("**Video Actions:**")
                        st.link_button("▶️ Watch on YouTube", url, type="primary", use_container_width=True)
                        
                        # Show clean URL
                        clean_url = url.split('&')[0] if '&' in url else url
                        st.markdown("**Video ID:**")
                        video_id = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', url)
                        if video_id:
                            st.code(video_id.group(1))
                    
                    if i < len(youtube_urls) - 1:
                        st.divider()
        else:
            st.warning("No YouTube URLs found in the search results")
            st.markdown("**Raw content:**")
            st.code(content)
            
    except Exception as e:
        st.error(f"Error displaying YouTube results: {str(e)}")
        st.markdown("**Raw content:**")
        st.code(str(content))

def display_wikipedia_results(content):
    """Enhanced display for Wikipedia results with better content handling"""
    st.markdown("### 📚 Wikipedia Article")
    
    content_str = str(content).strip()
    
    # Handle very long content
    if len(content_str) > 3000:
        # Show preview and full content in expandable section
        preview_content = content_str[:1000] + "..."
        
        # Split preview into paragraphs
        preview_paragraphs = preview_content.split('\n\n')
        
        # Show first paragraph as summary
        if preview_paragraphs:
            first_para = preview_paragraphs[0].strip()
            if first_para:
                st.info(f"**Summary:** {first_para}")
        
        # Show preview of remaining content
        st.markdown("**Preview:**")
        remaining_preview = '\n\n'.join(preview_paragraphs[1:3]) if len(preview_paragraphs) > 1 else ""
        if remaining_preview:
            st.markdown(remaining_preview)
        
        # Full content in expandable section
        with st.expander("📖 Show Full Article Content", expanded=False):
            # Split full content into manageable sections
            all_paragraphs = content_str.split('\n\n')
            
            for i, paragraph in enumerate(all_paragraphs):
                para = paragraph.strip()
                if para:
                    # Add section breaks for very long articles
                    if i > 0 and i % 5 == 0:
                        st.divider()
                    
                    # Format different types of content
                    if para.startswith('==') and para.endswith('=='):
                        # Wikipedia section headers
                        header = para.replace('=', '').strip()
                        st.markdown(f"#### {header}")
                    elif len(para) > 500:
                        # Very long paragraphs - break them up
                        sentences = para.split('. ')
                        for j in range(0, len(sentences), 3):
                            chunk = '. '.join(sentences[j:j+3])
                            if chunk:
                                st.markdown(chunk + ('.' if not chunk.endswith('.') else ''))
                    else:
                        st.markdown(para)
    
    else:
        # Regular display for shorter content
        paragraphs = content_str.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            para = paragraph.strip()
            if para:
                if i == 0:
                    # First paragraph as summary
                    st.info(f"**Summary:** {para}")
                elif para.startswith('==') and para.endswith('=='):
                    # Wikipedia section headers
                    header = para.replace('=', '').strip()
                    st.markdown(f"#### {header}")
                else:
                    st.markdown(para)
    
    # Content statistics
    word_count = len(content_str.split())
    char_count = len(content_str)
    
    st.caption(f"📊 **Article Stats:** {word_count:,} words • {char_count:,} characters")
    
    # Look for any image URLs
    image_urls = extract_image_urls(content_str)
    if image_urls:
        st.markdown("### 🖼️ Related Images")
        cols = st.columns(min(len(image_urls), 3))
        for i, img_url in enumerate(image_urls[:6]):  # Show up to 6 images
            with cols[i % 3]:
                try:
                    st.image(img_url, caption=f"Image {i+1}", width=200)
                except:
                    st.markdown(f"🖼️ [View Image]({img_url})")
    
    # Add Wikipedia source attribution
    st.markdown("---")
    st.caption("📖 Content sourced from Wikipedia • [Learn more about Wikipedia](https://www.wikipedia.org/)")

def display_tavily_results(content):
    """Enhanced display for Tavily search results"""
    try:
        # Handle both dict and string content
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                st.markdown("### 🔍 Search Results")
                st.markdown(str(content))
                return
        
        if isinstance(content, dict):
            # Display query info
            query = content.get('query', '')
            if query:
                st.markdown(f"### 🔍 Search Results for: *{query}*")
            else:
                st.markdown("### 🔍 Search Results")
            
            # Display answer if available
            answer = content.get('answer')
            if answer:
                st.info(f"**AI Summary:** {answer}")
            
            # Display results
            results = content.get('results', [])
            if results:
                st.markdown(f"**Found {len(results)} results:**")
                
                for i, item in enumerate(results[:8]):  # Show top 8 results
                    if isinstance(item, dict):
                        title = item.get('title', 'No title')
                        url = item.get('url', '')
                        snippet = item.get('content', '')
                        score = item.get('score', 0)
                        
                        # Create enhanced result cards
                        with st.container():
                            # Header with title and score
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"#### {i+1}. {title}")
                            with col2:
                                if score:
                                    # Show relevance score as stars
                                    stars = int(score * 5)
                                    st.markdown(f"{'⭐' * stars}{'☆' * (5-stars)}")
                            
                            # Content and source
                            if snippet:
                                st.markdown(f"📝 {snippet}")
                            
                            # Source and action buttons
                            if url:
                                col_source, col_button = st.columns([3, 1])
                                with col_source:
                                    domain = urlparse(url).netloc
                                    st.markdown(f"🌐 **Source:** [{domain}]({url})")
                                with col_button:
                                    st.link_button("🔗 Visit", url, type="secondary", use_container_width=True)
                            
                            st.divider()
            
            # Display images if available
            images = content.get('images', [])
            if images:
                st.markdown("### 🖼️ Related Images")
                cols = st.columns(min(len(images), 3))
                for i, img_url in enumerate(images[:6]):  # Show up to 6 images
                    with cols[i % 3]:
                        try:
                            st.image(img_url, caption=f"Image {i+1}", width=200)
                        except:
                            st.markdown(f"🖼️ [Image {i+1}]({img_url})")
            
            # Display follow-up questions if available
            follow_up = content.get('follow_up_questions', [])
            if follow_up:
                st.markdown("### 💡 Related Questions")
                for question in follow_up[:5]:
                    st.markdown(f"❓ {question}")
        
        elif isinstance(content, list):
            # Fallback for list format
            st.markdown("### 🔍 Search Results")
            for i, item in enumerate(content[:8]):
                if isinstance(item, dict):
                    title = item.get('title', 'No title')
                    url = item.get('url', '')
                    snippet = item.get('content', item.get('snippet', ''))
                    
                    with st.expander(f"📄 {i+1}. {title}"):
                        if snippet:
                            st.markdown(snippet)
                        if url:
                            st.markdown(f"🔗 **Source:** [{urlparse(url).netloc}]({url})")
        else:
            st.markdown("### 🔍 Search Results")
            st.markdown(str(content))
            
    except Exception as e:
        st.error(f"Error displaying Tavily results: {str(e)}")
        st.markdown("**Raw content:**")
        st.code(str(content))

def main():
    st.set_page_config(
        page_title="LangChain Tools Playground",
        page_icon="🎮",
        layout="wide"
    )
    
    st.title("🎮 LangChain Tools Playground")
    st.markdown("""
    **Learn and explore LangChain's pre-built tools through hands-on demonstrations.**
    
    This interactive application teaches you how to use LangChain's built-in tools for information retrieval. 
    Experience direct tool integration without LLM overhead - see how Wikipedia, YouTube, and Tavily search tools 
    work seamlessly with structured outputs and enhanced UI features.
    
    💡 **Perfect for learning:** No complex setups, just pure tool functionality demonstrations.
    
    📚 [Explore more LangChain tools](https://python.langchain.com/docs/integrations/tools/)
    """)
    
    # Initialize tools
    tools = initialize_tools()
    
    # Handle suggestion clicks
    if hasattr(st.session_state, 'suggested_query') and st.session_state.get('auto_execute', False):
        suggested_query = st.session_state.suggested_query
        st.session_state.auto_execute = False
        
        # Execute search with suggested query
        with st.spinner(f"Searching with {st.session_state.get('last_selected_tool', 'Wikipedia')}..."):
            result = execute_tool(suggested_query, st.session_state.get('last_selected_tool', 'Wikipedia'), tools)
            st.session_state.last_result = result
        
        st.success(f"✅ Searched for: '{suggested_query}'")
    
    # Create a form for better UX with CTRL+Enter support
    # Initialize reset counter for dynamic key
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
        
    with st.form(key=f"search_form_{st.session_state.reset_counter}", clear_on_submit=False):
        # User input section
        st.subheader("📝 Search Query")
        
        user_query = st.text_area(
            "Enter your search query:",
            placeholder="Ask anything you want to search for... (Press Ctrl+Enter to search)",
            height=100,
            key=f"search_input_{st.session_state.reset_counter}"
        )
        
        # Tool selection
        st.subheader("🛠️ Select Tool")
        selected_tool = st.radio(
            "Choose a tool for your search:",
            options=["Wikipedia", "YouTube", "Tavily"],
            horizontal=True,
            help="Each tool provides different types of information sources"
        )
        
        # Store selected tool for suggestions
        st.session_state.last_selected_tool = selected_tool
        
        # Control buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            execute_button = st.form_submit_button("🚀 Execute Search", type="primary", use_container_width=True)
        
        with col2:
            # Note: Reset button needs to be outside the form to work properly
            pass
        
        with col3:
            pass
    
    # Reset button outside the form
    reset_button = st.button("🔄 Reset", type="secondary")
    
    # Reset functionality
    if reset_button:
        # Clear search results
        if hasattr(st.session_state, 'last_result'):
            del st.session_state.last_result
        
        # Increment reset counter to create new widget with fresh state
        st.session_state.reset_counter += 1
        
        # Clear any suggestion states
        if hasattr(st.session_state, 'suggested_query'):
            del st.session_state.suggested_query
        if hasattr(st.session_state, 'auto_execute'):
            del st.session_state.auto_execute
            
        st.rerun()
    
    # Execute tool functionality
    if execute_button:
        # Validate input first
        is_valid, validation_message, suggestions = validate_search_input(user_query)
        
        if not is_valid:
            # Clear any previous results when validation fails
            if hasattr(st.session_state, 'last_result'):
                del st.session_state.last_result
                
            st.error(validation_message)
            
            # Show suggestions if available
            if suggestions:
                st.info("💡 **Did you mean:**")
                suggestion_cols = st.columns(min(len(suggestions), 3))
                for i, suggestion in enumerate(suggestions):
                    with suggestion_cols[i]:
                        if st.button(f"✨ {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                            # Store suggestion in session state and trigger a search
                            st.session_state.suggested_query = suggestion
                            st.session_state.auto_execute = True
                            st.rerun()
            
            # Show tool-specific examples
            if selected_tool in ["YouTube", "Wikipedia", "Tavily"]:
                examples = {
                    "YouTube": ["python tutorial", "cooking recipes", "music videos", "documentary films"],
                    "Wikipedia": ["artificial intelligence", "history of Rome", "climate change", "quantum physics"],
                    "Tavily": ["latest AI news", "weather forecast", "stock market updates", "current events"]
                }
                
                st.info(f"💡 **{selected_tool} Example Searches:**")
                example_cols = st.columns(2)
                for i, example in enumerate(examples[selected_tool]):
                    with example_cols[i % 2]:
                        st.markdown(f"• {example}")
        else:
            with st.spinner(f"Searching with {selected_tool}..."):
                result = execute_tool(user_query, selected_tool, tools)
                
                # Store result in session state
                st.session_state.last_result = result
    
    # Display results
    if hasattr(st.session_state, 'last_result'):
        display_enhanced_results(st.session_state.last_result)
    
    # Benefits and footer
    st.markdown("---")
    st.subheader("✨ Key Benefits")
    
    benefits = [
        "🚀 **No LLM calls required** - Direct tool integration using LangChain",
        "⚡ **Fast responses** - Direct API access without model inference delays",
        "🎯 **Structured output** - Consistent JSON formatting for all responses",
        "🔧 **Multiple sources** - Access Wikipedia, YouTube, and web search in one place",
        "💰 **Cost-effective** - No token usage for search operations",
        "🔒 **Secure** - API keys managed through environment variables"
    ]
    
    for benefit in benefits:
        st.markdown(benefit)
    
    # Sidebar with tool information
    with st.sidebar:
        st.header("🔍 Tool Information")
        
        tool_info = {
            "Wikipedia": {
                "description": "Access to Wikipedia's vast encyclopedia",
                "use_case": "Factual information, definitions, historical data"
            },
            "YouTube": {
                "description": "Search YouTube videos and content",
                "use_case": "Video content, tutorials, entertainment"
            },
            "Tavily": {
                "description": "Comprehensive web search engine",
                "use_case": "Current events, recent information, web content"
            }
        }
        
        for tool, info in tool_info.items():
            with st.expander(f"{tool} Tool"):
                st.write(f"**Description:** {info['description']}")
                st.write(f"**Best for:** {info['use_case']}")

if __name__ == "__main__":
    main()