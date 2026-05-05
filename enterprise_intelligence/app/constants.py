"""
Application-wide constants.

All configuration constants are defined here for easy modification
and centralized management.
"""

# Rate limiting
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60    # seconds

# Request/response validation
MAX_QUESTION_LENGTH = 5000
