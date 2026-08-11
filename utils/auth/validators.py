"""Email and name validation utilities."""

import re


def validate_email(email):
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, "Email format is valid"


def validate_full_name(full_name):
    """Validate full name."""
    if not full_name or len(full_name.strip()) < 2:
        return False, "Full name must be at least 2 characters long"
    
    if len(full_name) > 100:
        return False, "Full name must be less than 100 characters"
    
    return True, "Full name is valid"
