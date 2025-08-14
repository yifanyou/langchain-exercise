import getpass
import os
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

if not os.environ.get("DEEPSEEK_API_KEY"):
  os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for DeepSeek: ")

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# Create agent
print("-Create agent")

model = init_chat_model("deepseek-chat", model_provider="deepseek")

agent = create_react_agent(
    model=model,  
    tools=[get_weather],  
    prompt="You are a helpful assistant"  
)

# Run the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

for o in result["messages"]:
    if o.content != "":
        print(o.content)

# Configure llm
print("-Configure llm")

model = init_chat_model(
    "deepseek-chat",
    temperature=0
)

agent = create_react_agent(
    model=model,
    tools=[get_weather],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

for o in result["messages"]:
    if o.content != "":
        print(o.content)

#  Add a custom prompt
print("-Add a custom prompt")
print("--Static mode")

agent = create_react_agent(
    model=model,
    tools=[get_weather],
    # A static prompt that never changes
    prompt="Never answer questions about the weather."
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

for o in result["messages"]:
    if o.content != "":
        print(o.content)

print("--Dynamic mode")

from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState

def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:  
    user_name = config["configurable"].get("user_name")
    system_msg = f"You are a helpful assistant. Address the user as {user_name}."
    return [{"role": "system", "content": system_msg}] + state["messages"]

agent = create_react_agent(
    model=model,
    tools=[get_weather],
    prompt=prompt
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    config={"configurable": {"user_name": "John Smith"}}
)

for o in result["messages"]:
    if o.content != "":
        print(o.content)

# Add memory
print("Add memory")
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

agent = create_react_agent(
    model=model,
    tools=[get_weather],
    checkpointer=checkpointer  
)

# Run the agent
config = {"configurable": {"thread_id": "1"}}
sf_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    config  
)
ny_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what about new york?"}]},
    config
)
print("sf_response")
for o in sf_response["messages"]:
    if o.content != "":
        print(o.content)
print("ny_response")
for o in ny_response["messages"]:
    if o.content != "":
        print(o.content)

#Configure structured output
print("Configure structured output")
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    conditions: str

agent = create_react_agent(
    model=model,
    tools=[get_weather],
    response_format=WeatherResponse  
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

print(response["structured_response"])