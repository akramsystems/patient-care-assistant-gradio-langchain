def load_hospital_information():
    """Load hospital information from data_sheet.txt"""
    try:
        with open("data_sheet.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: data_sheet.txt not found")
        return ""


HOSPITAL_INFO = load_hospital_information()

