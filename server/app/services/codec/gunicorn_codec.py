import multiprocessing


bind = '0.0.0.0:7002'
loglevel = 'error'

if multiprocessing.cpu_count() < 2:
    cpu_count = 3
else:
    cpu_count = multiprocessing.cpu_count() * 2 + 1
workers = cpu_count

timeout = 120
backlog = 512
max_requests = 30000
max_requests_jitter = 2
limit_request_line = 1024
limit_request_fields = 256
limit_request_field_size = 1024
