from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv        # used to store secret stuff like API keys or configuration values
import os
import time

load_dotenv()

key=os.getenv("OPENAI_API_KEY")

class AgentState(TypedDict):
    messages: List[HumanMessage]

llm = ChatOpenAI(model="gpt-5-nano-2025-08-07",api_key=key)

def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])
    #temp=response.content
    #print(f"\nAI: {response.content}")
    for ele in response.content.split():
        print(ele,end=" ",flush=True)
        time.sleep(0.03)
    
    print()
    print(state)
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END) 
agent = graph.compile()

user_input = input("Enter: ")
while user_input != "exit":
    ans=agent.invoke({"messages": [HumanMessage(content=user_input)]})

    user_input = input("Enter: ")