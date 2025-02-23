from dotenv import load_dotenv; load_dotenv()
import requests

PATIENT_API_ENDPOINT = "http://localhost:5000/patient"
REQUIRED_FIELDS = {
    'name': "Enter patient's full name (First Last): ",
    'dob': "Enter date of birth (MM/DD/YYYY): ",
    'pcp': "Enter primary care provider (with title Dr/MD/DO): ",
    'ehrId': "Enter EHR ID (minimum 4 characters): "
}

def fetch_patient_data(patient_id: str) -> dict:
    """Fetch patient data from the API"""
    try:
        request_url = f"{PATIENT_API_ENDPOINT}/{patient_id}"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        print(f"Response details (if available): {getattr(e.response, 'text', 'N/A')}")  # Debug print
        return None