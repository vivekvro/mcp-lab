from fastapi import FastAPI
from mcp_servers.expense_tracker import mcp_ExpenseTracker

app = FastAPI()


import copy

servers = [mcp_ExpenseTracker]




@app.get("/tools")
async def return_all_tools():
    tools_for_llm = []

    for s in servers:
        tools = await s.list_tools()

        for t in tools:
            raw = t.parameters or {}

            # dig into nested structure
            schema = raw.get("properties", {}).get("parameters", {})

            schema = copy.deepcopy(schema)

            # remove config if exists
            if "properties" in schema:
                schema["properties"].pop("config", None)

            tools_for_llm.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": schema
                }
            })

    return tools_for_llm


@app.get("/tools/expensetracker")
async def return_ExpenseTracker_tools():
    tools_for_llm = []
    tools = await mcp_ExpenseTracker.list_tools()
    for t in tools:
        tools_for_llm.append({
            "type":"function",
            "function":{
                "name":t.name,
                "description":t.description,
                "parameters":t.parameters or {}
                }
            })
    return tools_for_llm