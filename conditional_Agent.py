from langgraph.graph import StateGraph,START,END
from typing import TypedDict


class AgentState(TypedDict):
    num1:int
    num2:int
    sign:str
    result:int=None#def->none  try  krna hai

def adder(state:AgentState)->AgentState:
    """add two inputs"""
    state['result']=state['num1']+state['num2']
    return state

def substractor(state:AgentState)->AgentState:
    """substract two inputs"""
    state['result']=state['num1']-state['num2']
    return state

def judge(state:AgentState):
    if state['sign']=='+':
        return "add"
    else:
        return "remove"

graph=StateGraph(AgentState)
graph.add_node("adder",adder)
graph.add_node("remover",substractor)
graph.add_node("middleman",lambda x:x)
graph.add_edge(START,"middleman")
graph.add_conditional_edges(
"middleman",
judge,
{
    "add":"adder",
    "remove":"remover"
}
)
graph.add_edge("adder",END)
graph.add_edge("remover",END)

app=graph.compile()

answer=app.invoke({"num1":1,"num2":2,"sign":'-'})
print(answer)