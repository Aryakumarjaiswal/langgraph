from typing import TypedDict
from langgraph.graph import StateGraph

# Define state structure
class AgentState(TypedDict):
    message: str

# Node function
def greet(state: AgentState) -> AgentState:
    state["message"] += " Welcome to LangGraph!"
    return state

# Build graph
graph = StateGraph(AgentState)
graph.add_node("greeting", greet)
graph.set_entry_point("greeting")
graph.set_finish_point("greeting")

# Compile and run
app = graph.compile()
result = app.invoke({"message": "User,"})
print(result)
