from prefect import task
from datetime import timedelta


@task(log_stdout=True, max_retries=5, retry_delay=timedelta(seconds=10))
def add_task(a, b):
    return a + b
