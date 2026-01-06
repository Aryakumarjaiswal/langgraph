from langchain_openai import ChatOpenAI
from langgraph.graph import START,StateGraph,END

from  langchain_core.tools import tool
from sqlalchemy import create_engine,text

from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from  typing import TypedDict,List,Union
import  os
from dotenv import load_dotenv
from pydantic import BaseModel,Field
from tavily import TavilyClient
load_dotenv()
key=os.getenv("OPENAI_API_KEY")

import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
load_dotenv()
MYSQL_USER =os.getenv("MYSQL_USER")
MYSQL_PASSWORD =os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT =os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)

try:
    engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # avoids stale connections
    pool_recycle=3600     # optional but good
)
    print("db connection established")
    
except Exception as  e:
    print("CONNECION FAILED",e)

class AgentState(TypedDict):

    messages:List[Union[HumanMessage, AIMessage]]
    search_result:str
    task_review:str





history=[]
llm=ChatOpenAI(model="gpt-5-nano-2025-08-07",api_key=key,max_retries=4)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class SQL_Output_Schema(BaseModel):
    sql_query:str=Field(description="Generate ready to run sql query (eg:select * from people;)")
    task_review:str=Field(description="Give a short review whether here about can we fulfill user request or not?")

class Executor_blueprint(BaseModel):
    executor_response:str=Field(description="If your response includes SQL query then just put SQL Query else put your clarification what you wanna ask to user")


def classifier(state:AgentState)->AgentState:
    """Via this node you've to classify user question into 1 of 4 categories """

    response = llm.invoke([SystemMessage( """
    For your reference you've past conversation history.Carefully see & analyse the past coversations and user input ,you've to classify the user input into either of independent,db_dependent,web_search_dependent or web_db_dependent class
    See below to decide :
    **independent**:Choose this, if you can be answer by just refering a past conversations.
    **db_dependent**:Choose this ,if you need to perform database operation .
    **web_search_dependent**:Choose this if to answer you need to do searching on internet.
    **web_db_dependent**:To answer you need to first do searching on an internet and then do insertion in database. 
    
    **NOTE**:Just return class name.

    """
)]+state["messages"])

 


    print(response.content)
    return response.content

def general(state:AgentState)->AgentState:
    response=llm.invoke(state["messages"])
    print(response.content)
    state["messages"].append(AIMessage(content=response.content))
    print("History till now")
    print(state["messages"])
    return state




def web_search(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    search = tavily.search(
        query=query,
        max_results=3
    )

    content = "\n".join(
        f"{r['title']}: {r['content']}"
        for r in search["results"]
    )
    state["search_result"]=content

    return state
    
def answer_web(state: AgentState) -> AgentState:
    response = llm.invoke(
        [SystemMessage(f"""User asked this question-> {state["messages"][-1].content } after doing web search we got this as a search result.see below
                    {state['search_result']}
                    please frame the answer in user friendly manner answering to his question.NOTE:Your answer will be send to end user so just  answer is  asked.
                       """)])
    print(response.content)
    state["messages"].append(AIMessage(content=response.content))
    state["search_result"]=""    
    print("History till now")
    print(state["messages"])
    return state

#             """
# You are a MySQL assistant who generates  best SQL query based on  user question.So here's the question {user_question}.see db information below
# people:databse table name .
# name:column  represents name of the person
# profession:column represents profession of the person
# location:column represents location of the person.

# just return ready to use sql query.
# - Return ONLY ONE valid MySQL SQL query
# - NO comments
# - NO multiple queries
# - NO explanations
# - The query MUST be executable using conn.execute()
# """

def db_crud_single_node(state: AgentState) -> AgentState:
    user_question = state["messages"][-1].content

    # 1️⃣ Generate SQL
    sql_response = llm.with_structured_output(SQL_Output_Schema).invoke([
        SystemMessage(
            f"""You're a task validator query  genertor.User asked {user_question}.To validate even if its  doable  or not,you've to generate validating SQL  query.
            Below table information
            # people:database table name .
            # name:column  represents name of the person
            # profession:column represents profession of the person
            # location:column represents location of the person.
            eg 1: If user asks to add/delete Ram with profession "Data Scientist" & location Mumbai  to check if same entry already exists you've generate best SQL Query eg: select * from people where name="Ram"  and give short review;
            eg 2: If user asks to change Ram's  profession from "Data Scientist" to "ML Engineer" then generate single SQL query to check does person name Ram with profession  "Data Scientist" exists if yes then arent there multiple  record or not and and give short review.
                                
            """

        )]+
     state["messages"]
    )

   
    #print("SQL Generated:", sql_response)
    sql_query = sql_response.sql_query.strip()
    validator_review=sql_response.task_review
    state["task_review"]=validator_review

    # 2️⃣ Execute SQL
    
    try:    
        with engine.begin() as conn:


            rows = conn.execute(text(sql_query)).fetchall()
            db_result = str(rows)
            #print(db_result)
          
    except Exception as e:
        raise RuntimeError("Could you give more clear version of your input")
    




                

    # 3️⃣ Explain result
    answer = llm.with_structured_output(Executor_blueprint).invoke([
        SystemMessage( f"""You're a task executor.User asked {user_question} and here's task validator's review {state['task_review']} and query response by it {db_result} .After analysing review & result please generate SQL Query 
                       if we can fulfill user request else generate message to user if you need any clarification but make sure you dont include    "select", "insert", "update", "delete",
    "from", "where", "join", "into",
    "values", "create", "drop", "alter" these keywords.
        
            Db information
            # people:database table name .
            # name:column  represents name of the person
            # profession:column represents profession of the person
            # location:column represents location of the person.
            Note:
                      If you'note writing  
                               
            """
)]+state["messages"]
      
        )
    import re

    SQL_KEYWORDS = [
    "*","select", "insert", "update", "delete",
    "from", "where", "join", "into",
    "values", "create", "drop", "alter"
]

    found = any(c.lower() in answer.executor_response.strip().lower() for c in SQL_KEYWORDS)
    print(found)
    if found:

        try:    
            with engine.begin() as conn:


                rows = conn.execute(text(sql_query)).fetchall()
                db_result = str(rows)

                #print(db_result)
                answer = llm.invoke([
                SystemMessage( f"""User asked {user_question} and here's task validator's review {state['task_review']} and after applying query we achieved user's requirement.
                              Notify customer that their request is fullfilled.
                               
            """
)]+state["messages"])
                state["messages"].append(AIMessage(content=answer.content))
                
        except:
            print("sorry request didtn fulfilled" )
            state["messages"].append(AIMessage(content="sorry request didtn fulfilled"))


    else:
        print("We cant perform this operation")
        state["messages"].append(AIMessage(content="We cant perform this operation"))
            
        

        


 
    

    
    

    #print(answer.executor_response)
    #state["messages"].append(AIMessage(content=answer.content))
    print("History till now")
    print(state["messages"])
    return state

graph=StateGraph(AgentState)
graph.add_node("no_problem",general)
graph.add_node("websearch",web_search)
graph.add_node("answerweb",answer_web)
graph.add_node("db_crud_single_node",db_crud_single_node)
graph.add_node("classify",lambda x:x)
graph.add_edge(START,"classify")
graph.add_conditional_edges("classify",classifier,{"independent":"no_problem","web_search_dependent":"websearch","db_dependent":"db_crud_single_node"})
graph.add_edge("no_problem",END)
graph.add_edge("websearch","answerweb")
graph.add_edge("answerweb",END)
graph.add_edge("db_crud_single_node",END)
agent=graph.compile()


llm=ChatOpenAI(model="gpt-5-nano-2025-08-07",api_key=key)
user_input=input("Enter Question-> ")
while user_input:

    history.append(HumanMessage(content=user_input))
                   
    agent.invoke({"messages":history})

    user_input = input("Enter: ")
################################33


