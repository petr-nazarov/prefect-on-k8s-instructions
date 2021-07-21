# Running a flow with custom modules on kubernetes.
It took me a while to figure out how to run code on prefect that is split in to multiple files (custom modules). I was getting an error:
```
UserWarning: Flow uses module which is not importable. Refer to documentation on how to import custom modules https://docs.prefect.io/api/latest/storage.html#docker
```
This is the way we solved it.
## Creating our code:
### poetry and pyenv
I will be using `poetry` to manage the dependencies of our project. And `pyenv` to manage the environment.
Run `pyenv install 3.8.9 ` if it is not yet installed and then run `pyenv local 3.8.9`
`poetry init` and set Compatible Python versions `python = "3.8.9"`
Run `poetry shell` to enter your virtual environment.
Install the dependencies:
`poetry add prefect`
## Writing code:
Lets we have following files:
`tasks/add_task.py`:
```py
from prefect import task
from datetime import timedelta

@task(log_stdout=True, max_retries=5, retry_delay=timedelta(seconds=10))
def add_task(a, b):
    return a + b
```

`tasks/multiply_task.py`:
```py
from prefect import task
from datetime import timedelta

@task(log_stdout=True, max_retries=5, retry_delay=timedelta(seconds=10))
def multiply_task(a, b):
    return a * b
```

`main.py`:
```
```


