from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage,HumanMessage,SystemMessage,BaseMessage

from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from requests import get


import asyncio
from typing import Annotated,Literal,TypedDict,List
from pydantic import Field
from  dotenv import load_dotenv
import json

load_dotenv()

model_name = "openai/gpt-oss-120b"
llm = ChatGroq(model=model_name,temperature=0)




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




async def build_graph():

# State
    class Chatstate(TypedDict):
        messages: Annotated[List[BaseMessage],add_messages]
# tool loading
    url ="http://127.0.0.1:8000/tools"
    response = get(url)
    tools =  response.json()
    llm_with_tools = llm.bind_tools(tools=tools)

    tool_node = ToolNode(tools=tools)


    # create chat_node
    async def chat_node(state:Chatstate):
        prev_msgs = state['messages']

        has_system = any(isinstance(msg, SystemMessage) for msg in prev_msgs)
        if not has_system:
            prev_msgs = [
                    SystemMessage(content="""
                                You are a helpful AI assistant. Assist users clearly, accurately, and in a polite, friendly tone.
                                  use tools when needed.

                                Guidelines:

                                * Use tools when necessary.
                                * Do not call tools if the question can be answered directly.
                                * Prefer concise and relevant responses.

                                """),

                ] + prev_msgs

        response = await llm_with_tools.ainvoke(prev_msgs)
        return {"messages":[response]}

    builder_graph = StateGraph(Chatstate)

    builder_graph.add_node("chat_node",chat_node)
    builder_graph.add_node("tools",tool_node)

    builder_graph.add_edge(START,"chat_node")
    builder_graph.add_conditional_edges("chat_node",tools_condition,{
    'tools':"tools", '__end__':END
    })
    

    return builder_graph.compile()





# main func
async def main():
    chatbot = await build_graph()


    user_input = str(input("Enter chat:   "))
    initial_state = {"messages":[HumanMessage(content=user_input)]}
    result = await chatbot.ainvoke(initial_state)

    print("Ai : ",result['messages'][-1].content)








    
    


    









    # tools_dict = {}
    # for tool in tools:
    #     tools_dict[tool.name] = tool





































if __name__=="__main__":

    asyncio.run(main())