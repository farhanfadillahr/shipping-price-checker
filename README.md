# 🚚 Indonesian Shipping Price Checker AI App

## Overview

This is an intelligent RAG (Retrieval-Augmented Generation) based AI application that helps users check shipping prices across Indonesia using the RajaOngkir API. The system combines function calling with LangChain, MistralAI, and vector database technology to provide an interactive and intelligent shipping cost calculation experience.

## 📁 Folder Structure

```
├──  Core_Application/
│   ├── streamlit_app.py      # Main Streamlit web interface
│   ├── cli.py                # Command-line interface
│   └── shipping_assistant.py # Main AI assistant orchestrator
│
├── 🔧 AI_And_Tools/
│   ├── shipping_tools.py     # LangChain function calling tools
│   ├── knowledge_base.py     # RAG vector database management
│   └── rajaongkir_api.py    # API client with error handling
│
├── 🐳 Deployment/
│   ├── Dockerfile           # Container configuration
│   ├── docker-compose.yml   # Multi-service orchestration
│   └── docker.sh           # Management script
│
├── 📚 Data_And_Config/
    ├── requirements.txt     # Python dependencies
    ├── chroma_db/          # Vector database storage
    ├── .env                # Environment variables
    ├── .env.example        # Environment template
    └── .dockerignore       # Docker build exclusions

```

## System Architecture & Flow

### Application Flow

1. **User Input**: User sends a query about shipping costs
2. **Intent Recognition**: AI assistant analyzes the query using RAG knowledge
3. **Information Extraction**: System identifies missing parameters (origin, destination, weight, etc.)
4. **Interactive Clarification**: If information is missing, bot asks specific questions
5. **Function Calling**: Once complete, system calls appropriate tools:
   - `search_destination`: Find location IDs
   - `calculate_shipping_cost`: Get shipping prices
6. **Result Formatting**: Raw API response is formatted into user-friendly output
7. **Knowledge Enhancement**: Interaction patterns are stored for future reference

## Technology Stack & Tools

### Core AI Technologies

| Tool/Library | Purpose | Usage in App |
|--------------|---------|--------------|
| **LangChain** | AI framework | Orchestrates the entire AI workflow, manages tools and chains |
| **MistralAI** | Language model | Powers the conversational AI and reasoning capabilities |
| **ChromaDB** | Vector database | Stores and retrieves shipping-related knowledge for RAG |
| **HuggingFace Embeddings** | Text embeddings | Converts text to vectors for similarity search |


### User Interfaces

| Interface | Technology | Purpose |
|-----------|------------|---------|
| **Web App** | Streamlit | Interactive web interface with chat, quick actions, weight converter |
| **CLI** | Python CLI | Terminal-based interaction for developers and power users |

### API Integration

#### RajaOngkir API Client (`rajaongkir_api.py`)
- **Base URL**: `https://api-sandbox.collaborator.komerce.id`
- **Authentication**: API Key based
- **Features**:
  - Location search with fuzzy matching
  - Multi-courier price calculation
  - Result formatting and error handling

### Knowledge Base (RAG System)

#### Components:
- **Vector Store**: ChromaDB for persistent storage
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Knowledge Types**:
  - Indonesian city/region information
  - Shipping weight guidelines
  - Courier service details
  - Common user query patterns
  - Troubleshooting information

#### RAG Process:
1. **Document Ingestion**: Shipping knowledge is chunked and embedded
2. **Query Processing**: User queries are embedded using same model
3. **Similarity Search**: Relevant knowledge chunks are retrieved
4. **Context Enhancement**: Retrieved context guides AI responses

## 🛠️ Manual Setup (Local Development)

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation Steps

#### Option 1: Direct Python (Development)
```bash
# From project root
cd "Core_Application"
streamlit run streamlit_app.py
```

##### Option 2: Docker (Production)
```bash
# From Deployment folder
cd Deployment
./docker.sh build
./docker.sh run
```

##### Option 3: Docker Compose
```bash
# From Deployment folder
cd Deployment
docker-compose up --build
```

## Usage Examples

Simply ask the bot about shipping prices:

- "What's the shipping cost from Jakarta to Surabaya for a 1kg package worth 100000?"
- "Check shipping prices to Bandung"
- "How much to send 500g item to Medan?"
- "Find locations named Jakarta"
- "Calculate shipping from Bandung to Yogyakarta, weight 2000g, value 500000"

The bot will guide you through the process and ask for any missing information.


##  Docker Services

The Docker Compose configuration includes:

- **shipping-app**: Main Streamlit web application (port 8501)
- **shipping-dev**: Development server with file watching (port 8502)
- **shipping-cli**: Interactive CLI interface


## 📄 License

This project is for educational and demonstration purposes.

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in docker-compose.yml
2. **Memory issues**: Increase Docker memory allocation
3. **API errors**: Check your internet connection and API credentials
4. **Container build fails**: Clear Docker cache with `docker system prune`