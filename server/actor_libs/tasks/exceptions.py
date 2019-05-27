from actor_libs.errors import ExceptionT


class TaskException(ExceptionT):

    def __init__(self, code, *, error_code=None, message=None):
        self.code = code
        self.error_code = error_code if error_code else 'TASK_ERROR'
        self.message = message if message else 'task error'

    def __call__(self, *args, **kwargs):
        return f"{self.error_code}: {self.message}"
