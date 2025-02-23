def get_user_input(prompt: str) -> str:
    """Helper function to handle user input with consistent quit behavior"""
    user_input = input(prompt)
    if user_input.lower() in ['quit', 'exit']:
        raise KeyboardInterrupt
    return user_input

