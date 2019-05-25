from actor_libs.configs import BaseConfig


project_config = BaseConfig().config
project_config['PUBLISH_TASK_URL'] = f"http://{project_config['TASK_SCHEDULER_NODE']}" \
                                     f"/api/v1/device_publish"
