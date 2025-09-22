from typing import TypedDict,List
from langgraph.graph import StateGraph
import time

class AgentState(TypedDict):
    message:str
    name:str
    age:int


def first_node(state:AgentState)->AgentState:
    
    state['message']=state['name']+"This is the first node"
    return state

def second_node(state:AgentState)->AgentState:
    
    state['message']=state['name']+" This is the second node"
    temp=state["message"]
    for ele in temp.split():
        print(ele,flush=True,end=" ")
        time.sleep(0.1)
    print()
    return state


graph=StateGraph(AgentState)
graph.add_node("f_node",first_node)
graph.add_node("s_node",second_node)
graph.set_entry_point("f_node")
graph.add_edge("f_node","s_node")
graph.set_finish_point("s_node")
app=graph.compile()


result=app.invoke({"message":"HI","name":"Arya","age":23})
print("last print statement",result)