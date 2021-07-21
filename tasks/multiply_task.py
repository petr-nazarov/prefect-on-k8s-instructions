from prefect import task
from datetime import timedelta


@task(log_stdout=True, max_retries=5, retry_delay=timedelta(seconds=10))
def multiply_task(a, b):
    return a * b
