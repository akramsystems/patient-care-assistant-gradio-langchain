import functools

from langgraph.types import Command, interrupt

from data_types import State, INITIAL_STATE, PatientData
from clients import fetch_patient_data, REQUIRED_FIELDS, llm_client
from utils import get_user_input

def log_entry_exit(func):
    """Decorator to log entry and exit of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Entering {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Exiting {func.__name__}")
        return result
    return wrapper




@log_entry_exit
def patient_data_validator(state: State) -> State:
    """Validate patient data and identify missing information"""
    # Handle Coming from missing info handler
    if state['feedback_required']:
        print("Patient data validator: Feedback required")
        state.update({
            'missing_info': [],
            'feedback_required': False
        })
        return state

    patient_data_dict = fetch_patient_data(state['patient_id'])
    if not patient_data_dict:
        return state
    
    state['patient_data'] = PatientData(**patient_data_dict)

    # **Recalculate missing fields dynamically**
    # For now this doesn't validate the quality of the data
    # just checks if the fields are empty
    missing_fields = [field for field in REQUIRED_FIELDS if not getattr(state['patient_data'], field).strip()]

    # Update state
    state.update({
        "missing_info": missing_fields,
        "feedback_required": bool(missing_fields)  # Set to False if no missing fields
    })
    return state


@log_entry_exit
def missing_info_handler(state: State) -> State:
    """Prompt the user for missing fields and update state"""
    # If no missing info, return to validation
    if not state['missing_info']:
        state['feedback_required'] = False
        return state  

    # Get the next missing field
    missing_field = state['missing_info'].pop(0)
    input_prompt = REQUIRED_FIELDS[missing_field]
    
    # Check if we already have stored user input
    user_input = interrupt(f"Please provide the {input_prompt} ")

    # Store the input
    if user_input.strip():
        updated_data = state['patient_data'].model_dump()  # Convert to dictionary for easy updates
        updated_data[missing_field] = user_input
        state['patient_data'] = PatientData(**updated_data)
        state['missing_info'].pop(0)  # Remove processed field

    # If more missing fields remain, pause again
    if state['missing_info']:
        state['pending_human_input'] = None  # Ensure we capture the next input
        return interrupt(f"Please provide the {REQUIRED_FIELDS[state['missing_info'][0]]}: ")

    return state  # Continue to patient_data_validator


@log_entry_exit
def care_recommendation_generator(state: State) -> State:
    """Generate care recommendations based on patient data and hospital context"""
    if state['missing_info']:
        return state
        
    patient_context = f"""
    Patient Information:
    - Name: {state['patient_data'].name}
    - DOB: {state['patient_data'].dob}
    - PCP: {state['patient_data'].pcp}
    - Recent Appointments: {state['patient_data'].appointments}
    - Referred Providers: {state['patient_data'].referred_providers}
    """
    
    response = llm_client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Based on this patient's information, provide care coordination recommendations and identify any concerning patterns: {patient_context}"
        }]
    )
    
    state["care_recommendations"] = response.choices[0].message.content

    state['feedback_required'] = False

    return state



