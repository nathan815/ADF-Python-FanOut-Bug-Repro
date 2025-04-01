from dataclasses import dataclass, field
import logging
import time
from typing import Any
import uuid
import azure.functions as func
import azure.durable_functions as df

# Workflows
define_workflows = [
    {
        "name": "workflow1",
        "steps": [
            {"name": "stepA", "success": ["stepB"]},
            {"name": "stepB", "success": ["stepC", "stepD", "stepE"]},
            {"name": "stepE"},
            {"name": "stepC", "success": ["stepF"]},
            {"name": "stepD", "success": ["stepG", "stepH"]},
            {"name": "stepF"},
            {"name": "stepG"},
            {"name": "stepH", "success": ["stepI"]},
            {"name": "stepI"}
        ]
    },
    {
        "name": "workflow2",
        "steps": [
            {"name": "stepA", "success": ["stepB", "stepC", "stepD", "stepE", "stepF"], "failure": ["stepZ"]},
            {"name": "stepB", "failure": ["stepZ"]},
            {"name": "stepC", "failure": ["stepZ"]},
            {"name": "stepD", "failure": ["stepZ"]},
            {"name": "stepE", "success": ["stepG", "stepH", "stepI"]},
            {"name": "stepF", "failure": ["stepZ"]},
            {"name": "stepG", "success": ["stepJ"], "failure": ["stepZ"]},
            {"name": "stepH", "failure": ["stepZ"]},
            {"name": "stepI", "failure": ["stepZ"]},
            {"name": "stepJ", "success": ["stepK", "stepL", "stepM"], "failure": ["stepZ"]},
            {"name": "stepK", "success": ["stepN"], "failure": ["stepZ"]},
            {"name": "stepL", "failure": ["stepZ"]},
            {"name": "stepM", "failure": ["stepZ"]},
            {"name": "stepN", "success": ["stepO", "stepP"], "failure": ["stepZ"]},
            {"name": "stepO", "success": ["stepQ", "stepR", "stepS"], "failure": ["stepZ"]},
            {"name": "stepP", "success": ["stepT"], "failure": ["stepZ"]},
            {"name": "stepQ", "failure": ["stepZ"]},
            {"name": "stepR", "failure": ["stepZ"]},
            {"name": "stepS", "failure": ["stepZ"]},
            {"name": "stepT", "success": ["stepU", "stepV"], "failure": ["stepZ"]},
            {"name": "stepU", "failure": ["stepZ"]},
            {"name": "stepV", "failure": ["stepZ"]},
            {"name": "stepZ"}
        ]
    },
    {
        "name": "workflow3",
        "steps": [
            {"name": "stepA", "success": ["stepB"]},
            {"name": "stepB", "success": ["stepC"]},
            {"name": "stepC", "success": ["stepD"]},
            {"name": "stepD", "success": ["stepE"]},
            {"name": "stepE", "success": ["stepF"]},
            {"name": "stepF", "success": ["stepG", "stepH"]},
            {"name": "stepG"},
            {"name": "stepH"}
        ]
    }
]

workflow_map = {w["name"]: w for w in define_workflows}

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@myApp.route(methods=["GET"], route="workflows/{workflowName}")
@myApp.durable_client_input(client_name="client")
async def start_workflow(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    workflow_name = req.route_params.get("workflowName", None)
    if not workflow_name or workflow_name not in workflow_map:
        return func.HttpResponse(f"Workflow '{workflow_name}' not found.", status_code=404)
    
    logging.info("Starting workflow_orchestrator for: %s", workflow_name)
    instance_id = await client.start_new("workflow_orchestrator", client_input=workflow_map[workflow_name])
    return client.create_check_status_response(req, instance_id)

@myApp.orchestration_trigger(context_name="context")
def workflow_orchestrator(context: df.DurableOrchestrationContext):
    workflow = context.get_input()
    logging.info(f"Starting execution of workflow: {workflow['name']}")

    step_map = {step["name"]: step for step in workflow["steps"]}

    queue = [("stepA", True)]  # (step_name, is_successful)
    while queue:
        tasks = []
        for step_name, is_successful in queue:
            step = step_map.get(step_name, {})

            # Determine next steps based on success/failure
            next_steps = step.get("success", []) if is_successful else step.get("failure", [])

            # Generate job ID and execute step
            job_id = yield context.call_activity("generate_job_id", step_name)
            step_result = context.call_sub_orchestrator("job_orchestrator", step_name)
            tasks.append((step_result, next_steps))  # Store next steps along with task

        # Wait for all tasks to complete
        results = yield context.task_all([t[0] for t in tasks])

        # Update queue with next steps based on results
        queue = []
        for (task_result, next_steps) in zip(results, [t[1] for t in tasks]):
            is_successful = task_result.get("succeeded", False)
            queue.extend([(step, is_successful) for step in next_steps])  # Include failure paths if needed

    return "Workflow completed"

@myApp.orchestration_trigger(context_name="context")
def job_orchestrator(context: df.DurableOrchestrationContext):
    step = context.get_input()
    logging.info(f"Executing job_orchestrator for step: {step}")
    result = yield context.call_activity("job_runner_activity", step)
    return result

@myApp.activity_trigger(input_name="input")
def job_runner_activity(input: str) -> dict:
    logging.info(f"Running step: {input}")
    time.sleep(2)
    return {"step": input, "succeeded": True}

@myApp.activity_trigger(input_name="input")
def generate_job_id(input: str) -> str:
    logging.info(f"Generating job id for step: {input}")
    return str(uuid.uuid4())
