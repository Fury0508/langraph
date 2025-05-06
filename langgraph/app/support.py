from graph import create_chat_graph
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command
import json
load_dotenv()
MONGODB_URI = "mongodb://admin:admin@localhost:27017"

config = {"configurable":{"thread_id":"3"}}
def init():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)
        # while True:
        #     user_input = input("> ")

        #     for event in graph_with_mongo.stream({"messages": [{"role":"user","content": user_input}]},config, stream_mode = "values"):
        #         if "messages" in event:
        #             event["messages"][-1].pretty_print()

        state = graph_with_mongo.get_state(config = config)

        # for message in state.values["messages"]:
        #     message.pretty_print()
        
        last_message = state.values['messages'][-1]
        tool_calls = last_message.additional_kwargs.get("tool_calls",[])

        user_query = None
        for call in tool_calls:
            if call.get("function",{}).get("name")== "human_assistance_tool":
                args = call["function"].get("arguments","{}")
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except:
                    print("Failed to decode function arguments")
        print("User is Trying to ask",user_query)
        ans = input("Resolution> ")

        resume_command = Command(resume={"data": ans})
        for event in graph_with_mongo.stream(resume_command,config,stream_mode = "values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
        # print("state",state.values['messages'])

init()