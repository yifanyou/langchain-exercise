from basic_llm import llm
from basic_type import State

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
