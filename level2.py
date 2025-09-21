from typing import List,TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    values:List[int]
    name:str
    result:str


def process_values(state:AgentState)->AgentState:
    """It  performs  operations on user input"""
    state['result']=f"{state['name']} your result is->{sum(state["values"])} "

    return state

graph=StateGraph(AgentState)
graph.add_node("processor",process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")
app=graph.compile()


answer=app.invoke({"values":[1,2,3,4],"name":"Aryakumar","result":"show result!!"})
print(answer)
print(answer['result'])