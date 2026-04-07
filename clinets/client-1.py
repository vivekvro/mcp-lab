from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage,HumanMessage,SystemMessage
from  dotenv import load_dotenv
load_dotenv()

model_name = "llama-3.3-70b-versatile"
llm = ChatGroq(model_name,temperature=0.713)