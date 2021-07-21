import prefect
from tasks.add_task import add_task
from tasks.multiply_task import multiply_task
from prefect import Flow
from storage import storageObj
from env import *
logger = prefect.context.get("logger")

with Flow(
    FLOW_NAME,
    storage=storageObj,
    run_config=KubernetesRun(),
    executor=DaskExecutor(
        cluster_class=lambda: KubeCluster(
            run_configuration.make_pod_spec(
                image=prefect.context.image
            )
        ),
        adapt_kwargs={"minimum": 5, "maximum": 20},
    ),
) as flow:
    a = add_task(5,5)
    b = multiply_task(a,20)
    logger.info(f"Result is {b}")


if __name__ == "__main__":
    flow.register(project_name=PROJECT_NAME)
    logger.info("Flow registered")
