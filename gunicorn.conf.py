# gunicorn.conf.py
bind = "0.0.0.0:8080"
workers = 2
timeout = 120
keepalive = 5
worker_class = "sync"
preload_app = True


# gunicorn.conf.py
import os
import multiprocessing

# Bind to the Railway provided port
bind = "0.0.0.0:8080"

# Calculate workers based on CPU cores, but limit for Railway
# Railway typically gives 2-4 CPUs, so use 1-2 workers
workers_per_core = int(os.environ.get('GUNICORN_WORKERS_PER_CORE', 1))
cpus = multiprocessing.cpu_count()
workers = min(workers_per_core * cpus, 2)  # Max 2 workers

# Force 1 worker for stability with your database
workers = 1  # Override to 1 to prevent connection issues

# Threads per worker - helps handle concurrent requests without more DB connections
threads = int(os.environ.get('GUNICORN_THREADS', 3))

# CRITICAL: Set preload_app to False
preload_app = False  # MUST be False to prevent connection inheritance

# Timeout settings
timeout = 120
keepalive = 5
graceful_timeout = 30

# Worker settings
worker_class = "sync"  # Use sync workers with threads

# Recycling workers prevents connection leaks
max_requests = 500
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')

# Environment variables
raw_env = [
    f'DJANGO_SETTINGS_MODULE=teba.settings',
    f'PYTHONPATH={os.getcwd()}',
]

# Post-fork hook to close database connections
def post_fork(server, worker):
    """Close database connections after fork to prevent sharing"""
    from django.db import connections
    for conn in connections.all():
        conn.close()
    
    # Also close any other connections that might have been inherited
    import gc
    gc.collect()
