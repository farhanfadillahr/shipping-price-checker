from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import os

class ShippingKnowledgeBase:
    """RAG knowledge base for shipping-related information"""
    
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            # Default to Data & Config/chroma_db relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_directory = os.path.join(project_root, "Data_And_Config", "chroma_db")
        self.persist_directory = persist_directory
        
        print("🔄 Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        print("✅ Embeddings model loaded!")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize or load existing vector store
        print("🔄 Initializing vector store...")
        self.vectorstore = self._initialize_vectorstore()
        print("✅ Vector store ready!")
    
    def _initialize_vectorstore(self):
        """Initialize vector store with shipping knowledge"""
        # Check if database already exists
        if os.path.exists(self.persist_directory):
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        
        # Create new database with initial knowledge
        documents = self._create_initial_documents()
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        vectorstore.persist()
        return vectorstore
    
    def _create_initial_documents(self) -> List[Document]:
        """Create initial documents for the knowledge base"""
        
        shipping_knowledge = [
            {
                "content": """
                Indonesian Shipping Regions and Areas:
                
                DKI Jakarta includes areas like Jakarta Pusat, Jakarta Utara, Jakarta Selatan, Jakarta Barat, Jakarta Timur.
                Common misspellings: Jakrta, Jakarata, Djakarta.
                
                Major cities in Java:
                - Surabaya (East Java) - often misspelled as Surabaja, Surubaya
                - Bandung (West Java) - sometimes written as Bandoeng
                - Semarang (Central Java)
                - Yogyakarta (DIY) - also known as Jogja, Jogjakarta
                - Malang (East Java)
                
                Major cities in Sumatra:
                - Medan (North Sumatra)
                - Palembang (South Sumatra)  
                - Padang (West Sumatra)
                - Pekanbaru (Riau)
                - Bandar Lampung (Lampung)
                """,
                "metadata": {"type": "location_info", "category": "indonesia_cities"}
            },
            {
                "content": """
                Shipping Weight Guidelines:
                
                Weight should be specified in grams:
                - 1 kg = 1000 grams
                - 500g = 0.5 kg
                - 2.5 kg = 2500 grams
                
                Common package weights:
                - Documents/letters: 50-200 grams
                - Books: 200-1000 grams
                - Clothing: 200-800 grams
                - Electronics (small): 500-2000 grams
                - Electronics (large): 2000-10000 grams
                
                If user mentions "small package", estimate 500g
                If user mentions "medium package", estimate 1000g
                If user mentions "large package", estimate 2000g
                """,
                "metadata": {"type": "shipping_info", "category": "weight_guidelines"}
            },
            {
                "content": """
                Item Value Guidelines:
                
                Item value affects insurance and COD options.
                Common item value ranges in Rupiah:
                
                - Documents: Rp 10,000 - Rp 50,000
                - Books: Rp 50,000 - Rp 200,000
                - Clothing: Rp 100,000 - Rp 500,000
                - Electronics: Rp 500,000 - Rp 10,000,000
                - Jewelry: Rp 1,000,000 - Rp 50,000,000
                
                If user doesn't specify value:
                - Ask for approximate item value
                - Explain that it affects insurance calculation
                - Suggest reasonable ranges based on item type
                """,
                "metadata": {"type": "shipping_info", "category": "item_value"}
            },
            {
                "content": """
                Courier Services Information:
                
                Available couriers and their characteristics:
                
                JNE (Jalur Nugraha Ekakurir):
                - Wide coverage across Indonesia
                - Services: CTC (City to City), CTCJTR (Cargo)
                - Reliable for inter-city shipping
                
                NINJA:
                - Fast growing courier service
                - Good for e-commerce
                - Standard service available
                
                SAP (SAP Express):
                - Cargo and regular services
                - UDRREG (Regular), DRGREG (Cargo)
                - Good for heavy items
                
                LION:
                - REGPACK service
                - Reliable for regular packages
                - Good coverage in major cities
                
                COD (Cash on Delivery) may not be available for all services.
                """,
                "metadata": {"type": "courier_info", "category": "service_types"}
            },
            {
                "content": """
                Common User Questions and Responses:
                
                Q: "How much to send to [city]?"
                A: Need to know: origin city, package weight, item value
                
                Q: "Shipping cost from [origin] to [destination]"
                A: Need to know: exact weight in grams, item value
                
                Q: "What's the cheapest shipping?"
                A: Compare all available options and highlight lowest cost
                
                Q: "Can I use COD?"
                A: Check COD availability in results, explain COD option
                
                Q: "How long for delivery?"
                A: Check ETD (Estimated Time Delivery) in results
                
                Always ask for clarification if:
                - Multiple locations match the search
                - Weight or value not specified
                - Origin or destination unclear
                """,
                "metadata": {"type": "faq", "category": "common_questions"}
            }
        ]
        
        documents = []
        for item in shipping_knowledge:
            doc = Document(
                page_content=item["content"],
                metadata=item["metadata"]
            )
            documents.append(doc)
        
        # Split documents into smaller chunks
        split_docs = self.text_splitter.split_documents(documents)
        return split_docs
    
    def search_knowledge(self, query: str, k: int = 3) -> List[Document]:
        """Search for relevant knowledge based on query"""
        return self.vectorstore.similarity_search(query, k=k)
    
    def add_knowledge(self, content: str, metadata: dict):
        """Add new knowledge to the database"""
        doc = Document(page_content=content, metadata=metadata)
        split_docs = self.text_splitter.split_documents([doc])
        
        self.vectorstore.add_documents(split_docs)
        self.vectorstore.persist()
    
    def get_context_for_query(self, query: str) -> str:
        """Get relevant context for a shipping query"""
        relevant_docs = self.search_knowledge(query, k=3)
        
        context = "Relevant shipping knowledge:\n\n"
        for doc in relevant_docs:
            context += f"- {doc.page_content}\n\n"
        
        return context
