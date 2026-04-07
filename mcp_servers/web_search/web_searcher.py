from langchain_groq import chat_models
from duckduckgo_search import DDGS
from langchain_core.messages import ToolMessage
from langchain_community.document_loaders import WebBaseLoader
from fastmcp import FastMCP
import asyncio
import random
mcp = FastMCP(name="web_search")
def get_random_proxy():
    proxies = [
        "http://ip1:port",
        "http://ip2:port",
        "http://ip3:port"
    ]
    return random.choice(proxies)

async def load_content(url):
    loader = WebBaseLoader(url,requests_kwargs={"headers": {"User-Agent": "Mozilla/5.0"}})
    docs = loader.load()
    return docs[0].page_content[:2000]


@mcp.tool()
async def web_search(query:str="No query given"):
    """ Web search tool.
    args:
    - query(string): Enter user's query for web search with current.
    * note all the queries could be based on recent events or historic.
    """
    def get_title_and_urls():
        with DDGS() as ddgs:
            res = list(ddgs.text(query,max_results=6))
        formatted = [{"title":x["title"],"url":x['href'] } for x in res ]
        return formatted

    try:
        title_n_urls = await asyncio.to_thread(get_title_and_urls)
    except Exception as e:
        return e




if __name__ == "__main__":
    mcp.run()