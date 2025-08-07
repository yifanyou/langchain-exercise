from langchain_openai import ChatOpenAI

from helper_utilies import make_supervisor_node

llm = ChatOpenAI(model="gpt-4o")

teams_supervisor_node = make_supervisor_node(llm, ["research_team", "writing_team"])