import uuid

from dotenv import load_dotenv; load_dotenv()
import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver; memory = MemorySaver()


from data_types import State, INITIAL_STATE
from nodes import (
    patient_data_validator, 
    missing_info_handler, 
    care_recommendation_generator,
)
from utils import get_user_input

def build_graph(State):
    graph_builder = StateGraph(State)
    # Add nodes
    def condition_validate_patient_data(state):
        if state['missing_info']:
            print("Routing to: Missing info handler")
            return "missing_info_handler"
        print("Routing to: Care recommendation generator")
        return "care_recommendation_generator"
    

    graph_builder.add_node("patient_data_validator", patient_data_validator)
    graph_builder.add_node("care_recommendation_generator", care_recommendation_generator)
    graph_builder.add_node("missing_info_handler", missing_info_handler)
    

    # Add edges with labels
    graph_builder.add_edge(START, "patient_data_validator")
    graph_builder.add_conditional_edges(
        "patient_data_validator",
        condition_validate_patient_data,
        {   
            "missing_info_handler": "missing_info_handler",
            "care_recommendation_generator": "care_recommendation_generator"
        }
    )
    graph_builder.add_edge("missing_info_handler", "patient_data_validator")
    graph_builder.add_edge("care_recommendation_generator", END)


    
    
    return graph_builder

graph_builder = build_graph(State)

graph = graph_builder.compile(
    checkpointer=memory,
)

# User Conversation ID
user_id = "123"
config = {"configurable": {"thread_id": user_id}}

    
# Print graph in ascii
# print(graph.get_graph().draw_ascii())

# Save graph to file
img_data = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(img_data)

print("\n=== Care Coordination System ===\n")


def process_request(message, history, user_id):
    config = {"configurable": {"thread_id": user_id}}

    # Get state
    state = graph.get_state(config=config).values
    if not state:
        state = INITIAL_STATE.copy()
        state.update({"patient_id": message})
        state["human_input"] = message
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "Validating patient data..."})
        graph.update_state(config=config, values=state)
    else:
        print("Getting Human Input")
        state["human_input"] = message
        history.append({"role": "user", "content": message})
        for event in graph.stream(None, config=config):
            graph.update_state(config=config, values=state)
    


    if "pending_human_input" in state:
        print("Pending human input")
        state["pending_human_input"] = message
        command = Command(resume=message)
    else:
        command = state

    for event in graph.stream(command, config=config):
        if '__interrupt__' in event:
            print("Event: Interrupt")
            if len(event['__interrupt__']) >= 1:
                ai_message = {
                    "role": "assistant", 
                    "content": event['__interrupt__'][0].value
                }

        elif "patient_data_validator" in event:
            print("Event: Patient data validator")
            if event["patient_data_validator"]["feedback_required"]:
                ai_message = {}
            else:
                ai_message = {
                    "role": "assistant", 
                    "content": "Patient data successfully validated."
                }
        elif "missing_info_handler" in event:
            print("Event: Missing info handler")
            pass
        elif "care_recommendation_generator" in event:
            print("Event: Care recommendation generator")
            ai_message = {
                "role": "assistant", 
                "content": event['care_recommendation_generator']['care_recommendations']
            }
        if ai_message:
            if history and history[-1].get("role") == "assistant" and history[-1].get("content") != ai_message["content"]:
                content = ""
                content += f"{history[-1]['content']}\n\n"
                content += f"{ai_message['content']}"
                ai_message["content"] = content
            history.append(ai_message)
            yield ai_message
    


user_id = gr.State(value=1)

demo = gr.ChatInterface(
    fn=process_request, 
    title="Care Provider Assistant",
    type="messages",
    autofocus=False,
    additional_inputs=[user_id],
    # theme="dark"
)

demo.launch()