
import bleach

def sanitize_input(input_str):
    if input_str is None:
        return ""
    return bleach.clean(input_str)