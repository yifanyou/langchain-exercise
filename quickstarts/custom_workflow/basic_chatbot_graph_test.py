from basic_chatbot_graph import graph

# Visualize the graph

# from IPython.display import Image, display

# try:
#     image_data = display(Image(graph.get_graph().draw_png()))
#     with open("basic_chatbot.png", "wb") as f:
#         f.write(image_data)
# except Exception:
#     # This requires some extra dependencies and is optional
#     pass

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break