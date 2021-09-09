import re
EMAIL_REGEX = r".*@.*\..*"

def name_constraint(name):
    return len(name) > 3

def email_constraint(email):
    return re.fullmatch(EMAIL_REGEX, email)

TEMPLATE = {
    "vars": {
        "name": {
            "type": "string",
            "constraint": {
                "func": name_constraint, 
                "error_message": 
                "Name needs to have at least 3 characters"
            }
        },
        "email": {
            "type": "string",
            "constraint": {
                "func": email_constraint, 
                "error_message": "Email is formatted wrong"
            }
        },
        "password": {
            "type": "binary"
        }
    }
}