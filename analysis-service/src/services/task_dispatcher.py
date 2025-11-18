import logging
from typing import Any, Dict
from src.models.project import AgentRole, ProjectBrief

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskDispatcher:
    """
    A prototype service for dispatching tasks to other agents.
    In a production environment, this would interface with a real task queue
    like Google Cloud Tasks.
    """

    async def dispatch_task(
        self,
        target_agent: AgentRole,
        brief: ProjectBrief,
        payload: Dict[str, Any] = None
    ):
        """
        Simulates dispatching a task to a target agent.
        
        :param target_agent: The role of the agent to dispatch the task to.
        :param brief: The project brief containing all necessary context.
        :param payload: Any additional data specific to this task.
        """
        if not payload:
            payload = {}
            
        logger.info(f"--- TASK DISPATCHED (PROTOTYPE) ---")
        logger.info(f"Target Agent: {target_agent.value}")
        logger.info(f"Project ID: {brief.project_id}")
        logger.info(f"Payload Keys: {list(payload.keys())}")
        logger.info(f"------------------------------------")
        
        # In a real implementation, this would create a Cloud Task:
        # e.g.,
        # client = tasks_v2.CloudTasksClient()
        # task = {
        #     "http_request": {
        #         "http_method": tasks_v2.HttpMethod.POST,
        #         "url": f"https://your-service-url/api/tasks/{target_agent.name.lower()}",
        #         "headers": {"Content-type": "application/json"},
        #         "body": brief.json().encode(),
        #     }
        # }
        # client.create_task(parent=queue_path, task=task)
        
        return {"status": "success", "message": f"Task for {target_agent.value} has been dispatched."}

# Singleton instance
task_dispatcher = TaskDispatcher()
