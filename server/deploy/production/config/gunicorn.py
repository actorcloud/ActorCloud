"""
All the settings are mentioned in the
settings(http://docs.gunicorn.org/en/latest/settings.html#settings) list
"""

bind = '0.0.0.0:7000'
workers = 9
loglevel = 'error'
timeout = 300
backlog = 1024
max_requests = 30000
max_requests_jitter = 2
limit_request_line = 1024
limit_request_fields = 256
limit_request_field_size = 1024
