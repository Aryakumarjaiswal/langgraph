from langchain_openai import ChatOpenAI
from langgraph.graph import START,END,StateGraph
from  langchain_core.tools import tool
from langchain_core.messages import BaseMessage,AIMessage,SystemMessage,ToolMessage
from dotenv import load_dotenv
from  typing import TypedDict,List
import os

load_dotenv()
key=os.getenv("OPENAI_API_KEY")

@tool
def add(a:int,b:int):
    """On recieving 2 numbers run this  function to add them"""
    return a+b


tools=[add]


llm=ChatOpenAI(model="gpt-5-nano-2025-08-07",api_key=key)

class AgentState(TypedDict):
    message:List[str]


def initial_tool(state:AgentState)->AgentState:
    system_prompt=SystemMessage(content="You're linked coach who teaches how  can one attract recruter via linkedin profile")
    response=llm.invoke([system_prompt+state["message"]])
    