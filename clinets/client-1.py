from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage,HumanMessage,SystemMessage
from  dotenv import load_dotenv
import asyncio

from typing import Annotated,Literal
from pydantic import Field
import json
load_dotenv()

# model_name = "llama-3.3-70b-versatile"
# llm = ChatGroq(model=model_name,temperature=0.713)



server_config_file_path = "configs/mcp_server_config.json"



# ----------------------  servers loader ------------------------------------------

async def load_servers():
    try:
        with open(server_config_file_path,'r') as f:
            servers = json.load(f)
        return servers
    except:
        return {}


# ---------------------- online server dumper ------------------------------------------
async def dump_cloud_servers(
        name:Annotated[str,Field(description="Name of the MCP Server.")]=None,
        transport:Literal["http","streamable_http","sse","websocket"]=None,
        url:Annotated[str,Field(description="url of MCP server")]=None
        ):
    # important checks before dump -------------------
    if not all([name ,transport, url]) :
        raise ValueError("Fill the required Fields")

    if transport not in ["http","streamable_http","sse","websocket"]:
        raise ValueError("Invalid transport")

    data = await load_servers()
    data[name]= {
            "transport":transport,
            "url":url
        }
        # try dumping, or return Error if not possible
    try:
        with open(server_config_file_path,"w") as f:
            json.dump(data,f,indent=4)
    except Exception as e:
        raise e



async def main():




    SERVERS = await load_servers()
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()

    tools_dict = {}
    for tool in tools:
        tools_dict[tool.name] = tool

    print(tools_dict)




































if __name__=="__main__":

    asyncio.run(main())