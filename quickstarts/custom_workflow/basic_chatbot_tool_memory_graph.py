from basic_chatbot_tool_graph import graph_builder
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

