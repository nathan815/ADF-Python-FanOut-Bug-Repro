from dataclasses import dataclass, field
import logging
import time
from typing import Any
import uuid
import azure.functions as func
import azure.durable_functions as df

# *** NOTE: See README.md


workflow1 = {
    "name": "workflow1",
    "steps": [
        {"name": "step1", "success": ["step2"]},
        {"name": "step2", "success": ["step3", "step4", "step2.2"]},
        {"name": "step2.2"},
        {"name": "step3", "success": ["step5"]},
        {"name": "step4", "success": ["step6", "step7"]},
        {"name": "step5"},
        {"name": "step6"},
        {"name": "step7", "success": ["step8"]},
        {"name": "step8"},
    ],
}

workflow2 = {
    "name": "workflow2",
    "steps": [
        {"name": "A", "success": ["B", "C", "D", "E", "F"], "failure": ["Z"]},
        {"name": "B", "failure": ["Z"]},
        {"name": "C", "failure": ["Z"]},
        {"name": "D", "failure": ["Z"]},
        {"name": "E", "success": ["G", "H", "I"]},
        {"name": "F", "failure": ["Z"]},
        {"name": "G", "success": ["J"], "failure": ["Z"]},
        {"name": "H", "failure": ["Z"]},
        {"name": "I", "failure": ["Z"]},
        {"name": "J", "success": ["K", "L", "M"], "failure": ["Z"]},
        {"name": "K", "success": ["N"], "failure": ["Z"]},
        {"name": "L", "failure": ["Z"]},
        {"name": "M", "failure": ["Z"]},
        {"name": "N", "success": ["O", "P"], "failure": ["Z"]},
        {"name": "O", "success": ["Q", "R", "S"], "failure": ["Z"]},
        {"name": "P", "success": ["T"], "failure": ["Z"]},
        {"name": "Q", "failure": ["Z"]},
        {"name": "R", "failure": ["Z"]},
        {"name": "S", "failure": ["Z"]},
        {"name": "T", "success": ["U", "V"], "failure": ["Z"]},
        {"name": "U", "failure": ["Z"]},
        {"name": "V", "failure": ["Z"]},
        {"name": "Y", "failure": ["Z"]},
        {"name": "Z"},
    ],
}

# A more linear workflow - no issues with this one
workflow3 = {
    "name": "workflow3",
    "steps": [
        {"name": "step1", "success": ["step2"]},
        {"name": "step2", "success": ["step3"]},
        {"name": "step3", "success": ["step4"]},
        {"name": "step4", "success": ["step5"]},
        {"name": "step5", "success": ["step6"]},
        {"name": "step6", "success": ["step7", "step8"]},
        {"name": "step7"},
        {"name": "step8"},
    ],
}

workflow_map = {w["name"]: w for w in [workflow1, workflow2, workflow3]}


myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@myApp.route(methods=["GET"], route="workflows/{workflowName}")
@myApp.durable_client_input(client_name="client")
async def start_workflow(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    workflow_name = req.route_params.get("workflowName", None)
    if not workflow_name:
        return func.HttpResponse(
            "Please provide a workflow name in the URL path.", status_code=400
        )

    try:
        workflow = workflow_map[workflow_name]
    except KeyError:
        logging.error(f"Workflow '{workflow_name}' not found.")
        return func.HttpResponse(
            f"Workflow '{workflow_name}' not found.", status_code=404
        )

    logging.info("Starting workflow_orchestrator DF for: %s", workflow_name)
    instance_id = await client.start_new("workflow_orchestrator", client_input=workflow)
    response = client.create_check_status_response(req, instance_id)
    return response


@myApp.orchestration_trigger(context_name="context")
def workflow_orchestrator(context: df.DurableOrchestrationContext):
    workflow = context.get_input()

    logging.info(f"Starting execution of workflow: {workflow['name']}")

    # Initialize the current step
    pending_steps = [workflow["steps"][0]]
    running_tasks: dict[str, Any] = {}
    completed_steps: list[dict] = []

    while pending_steps or running_tasks:
        # start all pending steps
        while pending_steps:
            step = pending_steps.pop(0)
            step_name = step["name"]

            new_job_id = "" #yield context.call_activity("generate_job_id", step_name)
            logging.info(
                f"Starting job_orchestrator sub-orch for step {step_name} with new ID {new_job_id} - step {step}"
            )
            task = context.call_sub_orchestrator("job_orchestrator", step)
            running_tasks[step_name] = task
            logging.info(f"Started job_orchestrator for step: {step_name} ID {new_job_id}")

        # wait for any running task to complete
        tasks = list(running_tasks.values())
        logging.info(f"Waiting for one of these tasks to complete: {running_tasks}")
        completed_task = yield context.task_any(tasks)
        logging.info(
            f"task_any returned task: {completed_task}"
        )  # Log which task completed
        step_result_out = completed_task.result

        if type(step_result_out) is not dict:
            # Handle unexpected result type
            logging.error(
                f"Unexpected result type: {type(step_result_out)}. Expected dict. step_result_out: {step_result_out}"
            )
            raise Exception(
                f"Unexpected result type from task_any. step_result: {step_result_out}"
            )

        step_result = step_result_out

        logging.info(f"Completed step: {step_result['step']}")
        completed_steps.append(step_result)
        del running_tasks[step_result["step"]["name"]]  # Remove from running tasks

        # Enqueue next steps based on the completed step
        next_steps = step_result["step"].get("always", []) + (
            step_result["step"].get("success", [])
            if step_result["succeeded"]
            else step_result["step"].get("failure", [])
        )

        for next_step_name in next_steps:
            next_step = next(
                (s for s in workflow["steps"] if s["name"] == next_step_name), None
            )
            if next_step and next_step not in pending_steps:
                # Only add to pending if it hasn't been started yet
                logging.info(f"Enqueuing next step: {next_step['name']}")
                pending_steps.append(next_step)
            else:
                logging.info(f"Skipping already pending step: {next_step['name']}")

    logging.info(
        f"Workflow is done. Completed step names: {[s['step']['name'] for s in completed_steps]}. Step results: {completed_steps}"
    )
    return "Workflow completed"


@myApp.orchestration_trigger(context_name="context")
def job_orchestrator(context: df.DurableOrchestrationContext):
    step = context.get_input()

    logging.info(
        f"job_orchestrator: Starting execution for step: {step['name']}. "
        f"Step details: {step}"
    )

    result = yield context.call_activity("job_runner_activity", step)

    logging.info(
        f"job_orchestrator: Received result for step: {step['name']}. Result: {result}"
    )

    return result


@myApp.activity_trigger(input_name="input")
def job_runner_activity(input: dict) -> dict:
    step = input
    logging.info(f"Running step: {step['name']}")
    time.sleep(2)  # Simulate some processing time
    return {"step": step, "succeeded": True}


@myApp.activity_trigger(input_name="input")
def generate_job_id(input: str) -> str:
    logging.info(f"Generating new job ID for step: {input}")
    return str(uuid.uuid4())
