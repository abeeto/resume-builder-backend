import multiprocessing

# The number of worker processes that will handle requests
# Following standard of (2 * number_of_cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# The address and port to bind the server to
bind = '0.0.0.0:8000'

# The log level to use for the server
# Common options: 'debug', 'info', 'warning', 'error', 'critical'
loglevel = 'info'

# max time worker can spend to handle a request (seconds)
timeout = 300
