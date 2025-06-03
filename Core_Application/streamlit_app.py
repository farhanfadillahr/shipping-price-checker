import os
import sys
import streamlit as st
import re

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shipping_assistant import create_shipping_assistant

# Set environment variables to prevent PyTorch issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Import warnings and suppress them
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Configure Streamlit page
st.set_page_config(
    page_title="Indonesian Shipping Price Checker",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main layout */
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    
    /* Chat container with better scrolling */
    .chat-container {
        height: 60vh;
        max-height: 600px;
        min-height: 400px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #fafafa;
        scroll-behavior: smooth;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        word-wrap: break-word;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #1f77b4;
        margin-left: 20%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
        border-left: 4px solid #00cc88;
        margin-right: 20%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Fixed chat input container */
    .chat-input-container {
        position: sticky;
        bottom: 0;
        # background: linear-gradient(to top, white 0%, white 70%, rgba(255,255,255,0.9) 100%);
        # padding: 1rem 0;
        # margin-top: 1rem;
        # border-top: 1px solid #e0e0e0;
        z-index: 1000;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        background-color: #2a4636;
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    
    .feature-box {
        background: #2a4636;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Quick actions with collapsible sections */
    .quick-actions {
        background-color: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .collapsible-section {
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 15px;
        overflow: hidden;
        background-color: white;
    }
    
    .collapsible-header {
        background: linear-gradient(135deg, #f7f7f7 0%, #e9ecef 100%);
        padding: 12px 15px;
        cursor: pointer;
        border-bottom: 1px solid #ddd;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.3s ease;
    }
    
    .collapsible-header:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    
    .toggle-icon {
        font-size: 16px;
        transition: transform 0.3s ease;
    }
    
    .collapsible-header.active .toggle-icon {
        transform: rotate(90deg);
    }
    
    .collapsible-content {
        padding: 15px;
        display: none;
        animation: slideDown 0.3s ease;
    }
    
    @keyframes slideDown {
        from { opacity: 0; max-height: 0; }
        to { opacity: 1; max-height: 200px; }
    }
    
    .collapsible-content.active {
        display: block;
    }
    
    /* Button improvements */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #ddd;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Mobile-first responsive design */
    .chat-container {
        height: 60vh;
        min-height: 400px;
    }
    
    .user-message {
        margin-left: 2%;
        margin-right: 10%;
        font-size: 14px;
    }
    
    .assistant-message {
        margin-left: 10%;
        margin-right: 2%;
        font-size: 14px;
    }
    
    .chat-message {
        padding: 0.8rem;
        margin-bottom: 0.8rem;
    }
    
    .quick-actions {
        padding: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    .collapsible-header {
        padding: 12px 15px;
        font-size: 14px;
    }
    
    .collapsible-content {
        padding: 12px;
    }
    
    .stButton > button {
        font-size: 13px;
        padding: 0.4rem 0.8rem;
        height: auto;
        min-height: 38px;
    }
    
    /* Main content padding for mobile */
    .css-18e3th9 {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* Sidebar adjustments */
    .css-1d391kg {
        width: 280px;
    }
    
    /* Header responsiveness */
    .main-header h1 {
        font-size: 1.8rem !important;
        margin-bottom: 15px;
    }
    
    .main-header p {
        font-size: 14px;
        margin-bottom: 20px;
    }
    
    /* Chat input improvements */
    .stChatInput > div {
        border-radius: 25px;
    }
    
    .stChatInput input {
        font-size: 14px;
        padding: 12px 16px;
    }
    
    /* Expander styling for mobile */
    .streamlit-expanderHeader {
        font-size: 16px;
        font-weight: 600;
        padding: 12px 0;
    }
    
    /* Columns adjustments */
    .css-ocqkz7 {
        gap: 0.5rem;
    }
    
    /* Number input adjustments */
    .stNumberInput > div > div > input {
        font-size: 14px;
        padding: 8px 12px;
    }
    
    /* Metric styling */
    .css-1xarl3l {
        font-size: 14px;
    }
    
    /* Very small screens */
    @media (max-width: 480px) {
        .chat-container {
            height: 55vh;
            min-height: 300px;
        }
        
        .user-message, .assistant-message {
            margin-left: 0%;
            margin-right: 0%;
            font-size: 13px;
        }
        
        .chat-message {
            padding: 0.6rem;
        }
        
        .main-header h1 {
            font-size: 1.4rem !important;
        }
        
        .stButton > button {
            font-size: 12px;
            padding: 0.3rem 0.6rem;
            min-height: 35px;
        }
        
        .collapsible-header {
            padding: 10px 12px;
            font-size: 13px;
        }
        
        .css-1d391kg {
            width: 260px;
        }
    }
    
    /* Weight converter styling */
    .weight-converter {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffcc02;
        margin: 0.5rem 0;
    }
    
    /* Value options styling */
    .value-option {
        margin: 0.3rem 0;
    }
    
    /* Scroll to bottom button */
    .scroll-bottom {
        position: absolute;
        bottom: 80px;
        right: 20px;
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 999;
    }
    
    .scroll-bottom:hover {
        background-color: #1565c0;
        transform: scale(1.1);
    }
</style>

<script>
function toggleCollapsible(element) {
    const content = element.nextElementSibling;
    const isActive = content.classList.contains('active');
    
    // Close all other collapsible sections
    document.querySelectorAll('.collapsible-content').forEach(c => {
        c.classList.remove('active');
    });
    document.querySelectorAll('.collapsible-header').forEach(h => {
        h.classList.remove('active');
    });
    
    // Toggle current section
    if (!isActive) {
        content.classList.add('active');
        element.classList.add('active');
    }
}

// Auto-scroll to bottom of chat
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Auto-scroll when new message is added
setTimeout(scrollToBottom, 100);
</script>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'assistant' not in st.session_state:
        with st.spinner("Initializing shipping assistant..."):
            st.session_state.assistant = create_shipping_assistant()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_msg = """
        🚚 **Welcome to Indonesian Shipping Price Checker!**
        
        I'm your AI assistant for checking shipping costs across Indonesia using the Rajaongkir API.
        
        **How I can help:**
        - 🔍 Find shipping costs between any two locations in Indonesia
        - 📊 Compare prices from multiple couriers (JNE, NINJA, SAP, LION, etc.)
        - ⏱️ Check delivery times and COD availability
        - 📍 Help you find the right location IDs for accurate pricing
        
        **To get started, just tell me:**
        - 📍 Where you want to ship from and to
        - ⚖️ Package weight (in grams or kg)
        - 💰 Item value (in Rupiah)
        
        **Example:** "What's the shipping cost from Jakarta to Surabaya for a 1kg package worth Rp 500,000?"
        
        Try asking me about shipping costs or use the Quick Actions!
        """
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

def display_chat_history():
    """Display chat history using proper Streamlit components"""
    
    # Create chat container
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            # User message with custom styling
            with st.chat_message("user", avatar="🧑"):
                st.markdown(message["content"])
        else:
            # Assistant message with custom styling  
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
    
    # Auto-scroll JavaScript
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo(0, document.body.scrollHeight);
        }, 100);
    </script>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown("""
    <h1 class="main-header">🚚 Indonesian Shipping Price Checker</h1>
    <p style="text-align: center; color: #666; margin-bottom: 30px;">
        AI-powered shipping cost calculator using Rajaongkir API with RAG
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Quick Guide")
        
        st.markdown("""
        <div class="sidebar-content">
            <h4>🎯 What You Need:</h4>
            <ul>
                <li><strong>📍 Origin:</strong> Where you're shipping from</li>
                <li><strong>🎯 Destination:</strong> Where you're shipping to</li>
                <li><strong>⚖️ Weight:</strong> Package weight in grams/kg</li>
                <li><strong>💰 Value:</strong> Item value in Rupiah</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h4>✨ Features:</h4>
            <ul>
                <li>Smart location search</li>
                <li>Multiple courier comparison</li>
                <li>COD availability check</li>
                <li>Delivery time estimates</li>
                <li>AI-powered assistance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📝 Example Queries")
        
        example_queries = [
            "Shipping cost Jakarta to Bandung 1kg Rp 200,000",
            "How much to send 500g to Surabaya?",
            "Compare shipping from Medan to Yogyakarta",
            "What's the cheapest option to Bali?",
            "Fastest delivery to Makassar?"
        ]
        
        for i, query in enumerate(example_queries):
            if st.button(query, key=f"example_{i}", use_container_width=True):
                st.session_state.user_input = query.split(" ", 1)[1]  # Remove emoji
                st.rerun()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.session_state.assistant.reset_conversation()
                # Re-add welcome message
                welcome_msg = """
                🚚 **Conversation cleared!**
                
                I'm ready to help you with new shipping cost inquiries. 
                Just ask me about shipping costs between any locations in Indonesia! 🇮🇩
                """
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                st.rerun()
        
        with col2:
            if st.button("ℹ️ Help", use_container_width=True):
                help_msg = """
                🤖 **How to use this bot:**
                
                1. **Simple format:** "From [Origin] to [Destination] weight [Weight] value [Value]"
                2. **Natural language:** "What's shipping cost from Jakarta to Bali for 2kg package?"
                3. **Use Quick Actions** for common origins and values
                4. **Weight converter** helps convert kg to grams
                
                **Tips:**
                - Be specific with city names
                - Include package weight and value for accurate quotes
                - Try different couriers for best prices
                - Check COD availability if needed
                """
                st.session_state.messages.append({"role": "assistant", "content": help_msg})
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 12px;">
            <p>🚚 Powered by RajaOngkir API<br>
            🤖 Built with LangChain & MistralAI<br>
            📊 RAG-enabled knowledge base</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat interface - Mobile-optimized single column layout
    
    # Display chat history
    display_chat_history()
    
    # Chat input container
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    user_input = st.chat_input("Ask about shipping costs... (e.g., 'Jakarta to Surabaya 1kg Rp 500000')")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions in expandable section for mobile
    with st.expander("🎯 Quick Actions", expanded=False):
        render_quick_actions()
    
    # Handle pre-filled input from example buttons
    if hasattr(st.session_state, 'user_input'):
        user_input = st.session_state.user_input
        delattr(st.session_state, 'user_input')
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get assistant response
        with st.spinner("🤖 Checking shipping costs..."):
            try:
                # Check if assistant is properly initialized
                if not hasattr(st.session_state, 'assistant') or st.session_state.assistant is None:
                    st.error("Assistant not properly initialized. Please refresh the page.")
                    return
                
                response = st.session_state.assistant.chat(user_input)
                
                # Validate response
                if not response or not isinstance(response, str):
                    response = "❌ I couldn't generate a proper response. Please try again with a different query."
                
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"❌ Sorry, I encountered an error: {str(e)}. Please try again with a different query."
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                # Log error to console for debugging
                st.error(f"Debug error: {type(e).__name__}: {str(e)}")
        
        # Rerun to update the display
        st.rerun()

def render_quick_actions():
    """Render quick actions section - mobile optimized"""
    
    # Common Origins - Always expanded for mobile
    st.markdown("**📍 Common Origins:**")
    common_origins = ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Yogyakarta"]
    
    # Use 3 columns for mobile layout
    cols = st.columns(3)
    for i, city in enumerate(common_origins):
        with cols[i % 3]:
            if st.button(f"📍 {city}", key=f"origin_{city}", use_container_width=True):
                st.session_state.user_input = f"Shipping from {city}"
                st.rerun()
    
    st.markdown("---")
    
    # Weight Converter - Compact for mobile
    st.markdown("**📦 Weight Converter:**")
    col1, col2 = st.columns([2, 1])
    with col1:
        weight_kg = st.number_input("Weight (kg):", min_value=0.0, max_value=100.0, step=0.1, value=1.0, key="weight_input")
    with col2:
        weight_grams = weight_kg * 1000
        st.metric("Grams", f"{weight_grams:,.0f}")
    
    if st.button("📦 Use this weight", key="use_weight", use_container_width=True):
        st.session_state.user_input = f"Package weight {weight_grams:,.0f} grams"
        st.rerun()
    
    st.markdown("---")
    
    # Common Item Values - Compact grid for mobile
    st.markdown("**💰 Common Item Values:**")
    value_options = {
        "📄 Document": 25000,
        "📚 Book": 100000,
        "👕 Clothing": 300000,
        "📱 Phone": 1000000,
        "💻 Laptop": 5000000
    }
    
    # Use 2 columns for value options
    cols = st.columns(2)
    for i, (item_type, value) in enumerate(value_options.items()):
        with cols[i % 2]:
            if st.button(f"{item_type}\nRp {value:,}", key=f"value_{item_type}", use_container_width=True):
                st.session_state.user_input = f"Item value Rp {value:,}"
                st.rerun()
    
    # Add JavaScript for mobile UX
    st.markdown("""
    <script>
    // Scroll to bottom of chat when page loads
    window.addEventListener('load', function() {
        setTimeout(scrollToBottom, 500);
    });
    
    // Handle mobile orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(scrollToBottom, 800);
    });
    
    // Mobile-specific optimizations
    document.addEventListener('DOMContentLoaded', function() {
        // Add touch-friendly interactions
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.95)';
            });
            button.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            });
        });
        
        // Improve scroll behavior on mobile
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.style.scrollBehavior = 'smooth';
        }
    });
    
    // Handle virtual keyboard on mobile
    window.addEventListener('resize', function() {
        if (window.innerHeight < 500) {
            // Virtual keyboard is likely open
            const chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                chatContainer.style.height = '40vh';
            }
        } else {
            // Virtual keyboard is likely closed
            const chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                chatContainer.style.height = '60vh';
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
