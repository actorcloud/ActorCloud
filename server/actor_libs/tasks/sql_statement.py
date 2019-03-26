insert_task_sql = """
 INSERT INTO actor_tasks
 ("createAt", "taskID", "taskStatus", "taskName", "taskInfo")
 VALUES('{createAt}', '{taskID}', {taskStatus}, '{taskName}', '{taskInfo}')
"""

update_task_sql = """
UPDATE "actor_tasks" 
  SET "updateAt"='{updateAt}', 
      "taskStatus"={taskStatus},
      "taskProgress"={taskProgress},
      "taskResult"='{taskResult}'
WHERE "taskID"='{taskID}'
"""
