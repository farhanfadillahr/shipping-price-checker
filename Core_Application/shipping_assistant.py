import os
import sys
import re
from typing import Dict, Any
from dotenv import load_dotenv

# Add AI & Tools directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AI_And_Tools"))

from langchain_mistralai import ChatMistralAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage
from shipping_tools import create_shipping_tools
from knowledge_base import ShippingKnowledgeBase

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data_And_Config", ".env"))

class ShippingAssistant:
    """Main shipping assistant class that combines RAG and function calling"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            temperature=0.1,
            mistral_api_key=os.getenv("MISTRAL_API_KEY")
        )
        
        # Initialize knowledge base
        self.knowledge_base = ShippingKnowledgeBase()
        
        # Initialize tools
        self.tools = create_shipping_tools()
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=20  # Keep last 20 exchanges
        )
        
        # Create agent
        self.agent_executor = self._create_agent()
        
    def _create_agent(self):
        """Create the LangChain agent with tools and prompt"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _get_system_prompt(self):
        """Get the system prompt for the assistant"""
        return """
        You are a helpful shipping assistant for Indonesia. Your job is to help users calculate shipping costs using the Rajaongkir API.

        IMPORTANT GUIDELINES:
        1. Always be polite and helpful
        2. Ask for clarification when information is missing or unclear
        3. When users mention locations, use the search_destination tool to find exact matches
        4. If multiple locations match, present options and ask user to choose
        5. Always require ALL necessary parameters before calculating costs:
           - Origin location ID
           - Destination location ID  
           - Weight in grams
           - Item value in Rupiah
        6. Provide clear, formatted results with all shipping options
        7. Explain COD availability and delivery times
        8. Help users understand weight conversions (kg to grams)
        9. Suggest reasonable item values if not provided

        CONVERSATION FLOW:
        1. Greet the user and ask what they want to ship
        2. Get origin and destination (search if needed)
        3. Get package weight and item value
        4. Calculate and present shipping options
        5. Answer any follow-up questions

        WHEN TO ASK FOR CLARIFICATION:
        - Location names that return multiple results
        - Missing weight or item value
        - Unclear package descriptions
        - Ambiguous location names

        Always use the knowledge base context to provide accurate information about Indonesian locations and shipping guidelines.
        """
    
    def _enhance_query_with_context(self, user_input: str) -> str:
        """Enhance user query with relevant context from knowledge base"""
        context = self.knowledge_base.get_context_for_query(user_input)
        
        enhanced_input = f"""
        User Query: {user_input}
        
        {context}
        
        Based on the above context and user query, please help the user with their shipping inquiry.
        """
        
        return enhanced_input
    
    def chat(self, user_input: str) -> str:
        """Main chat interface"""
        try:
            # Enhance query with RAG context
            enhanced_input = self._enhance_query_with_context(user_input)
            
            # Get response from agent
            result = self.agent_executor.invoke({
                "input": enhanced_input
            })
            
            return result["output"]
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
    
    def reset_conversation(self):
        """Reset the conversation memory"""
        self.memory.clear()
    
    def get_conversation_history(self):
        """Get the current conversation history"""
        return self.memory.chat_memory.messages
    
    def extract_shipping_info(self, text: str) -> Dict[str, Any]:
        """Extract shipping information from user text using regex"""
        info = {}
        
        # Extract weight patterns
        weight_patterns = [
            r'(\d+(?:\.\d+)?)\s*kg',
            r'(\d+(?:\.\d+)?)\s*kilogram',
            r'(\d+(?:\.\d+)?)\s*gram',
            r'(\d+(?:\.\d+)?)\s*g\b'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, text.lower())
            if match:
                weight_value = float(match.group(1))
                if 'kg' in pattern or 'kilogram' in pattern:
                    info['weight'] = weight_value * 1000  # Convert to grams
                else:
                    info['weight'] = weight_value
                break
        
        # Extract value patterns
        value_patterns = [
            r'rp\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'rupiah\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*rupiah'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, text.lower())
            if match:
                value_str = match.group(1).replace(',', '')
                info['item_value'] = float(value_str)
                break
        
        # Extract location patterns
        location_keywords = ['dari', 'from', 'ke', 'to', 'menuju', 'asal']
        for keyword in location_keywords:
            pattern = f'{keyword}\\s+([A-Za-z\\s]+?)(?:\\s+(?:ke|to|menuju)|$)'
            match = re.search(pattern, text.lower())
            if match:
                location = match.group(1).strip()
                if keyword in ['dari', 'from', 'asal']:
                    info['origin'] = location
                else:
                    info['destination'] = location
        
        return info

# Convenience function to create assistant instance
def create_shipping_assistant():
    """Create a new shipping assistant instance"""
    return ShippingAssistant()
