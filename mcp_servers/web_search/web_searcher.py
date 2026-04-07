from langchain_groq import chat_models
from duckduckgo_search import DDGS
from langchain_core.messages import ToolMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain_groq  import ChatGroq

from fastmcp import FastMCP
import asyncio
import random
from dotenv import load_dotenv

load_dotenv()



summarizer_llm = ChatGroq(model="llama-3.1-8b-instant",temperature=0.723)


mcp = FastMCP(name="web_search")



async def load_content(url):
    try:
        loader = WebBaseLoader(url,requests_kwargs={"headers": {"User-Agent": "Mozilla/5.0"}})
        docs = await loader.aload()
        return docs[0].page_content[:1500]
    except:
        return "failed to load content"

async def summarize_webpage(query:str,web_content):
    prompt = f"""Your work is to summarize given web page's content on basis of given user query:
    user query : {query}
    --------------------------------
    web page content: {web_content}
    --------------------------------
    summary should be in less words as possible
    """

    result = await summarizer_llm.ainvoke(prompt)
    return result.content


async def summarize(query:str,summaries:list[str]):
    summaries_text = "\n\n".join([s for s in summaries if s])
    prompt = f""" Your work is to create a final Summary with all summaries of web pages for the user query:
    user query - {query}

    summaries - {summaries_text}
    """

    result = await summarizer_llm.ainvoke(prompt)
    return result.content


semaphore = asyncio.Semaphore(3)

async def process_url(query:str,url):
    async with semaphore :
        content = await load_content(url)
        if content=="failed to load content":
            return None
        return await summarize_webpage(query,content)


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
        urls = await asyncio.to_thread(get_title_and_urls)
        summaries = await asyncio.gather(*[process_url(query,url['url']) for url in urls])
        return await summarize(query,summaries)
    except Exception as e:
        return str(e)




if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8002)