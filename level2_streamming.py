
from typing import List,TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    values:List[int]
    name:str
    result:str


import time

def process_values(state: AgentState) -> AgentState:
    result = f"{state['name']} your result is -> {sum(state['values'])}"
    
    # Simulate streaming word by word
    state['result'] = ""
    for word in result.split():
        print(word, end=' ', flush=True)
        time.sleep(0.3)  # adjust speed as needed
        state['result'] += word + " "
    
    print()  # for clean newline after stream
    return state


graph=StateGraph(AgentState)
graph.add_node("processor",process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")
app=graph.compile()


answer=app.invoke({"values":[1,2,3,4],"name":"Aryakumar","result":"show result!!"})
