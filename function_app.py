from dataclasses import dataclass, field
from http import HTTPMethod
import logging
import time
from typing import Any
import azure.functions as func
import azure.durable_functions as df

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@dataclass
class WorkflowStep:
    name: str
    always: list["WorkflowStep"] = field(default_factory=list)
    success: list["WorkflowStep"] = field(default_factory=list)
    failure: list["WorkflowStep"] = field(default_factory=list)

    def to_json(self):
        return self.__dict__

    def from_json(json_data):
        return WorkflowStep(**json_data)


@dataclass
class StepResult:
    step: WorkflowStep
    succeeded: bool

    def next_steps(self) -> list[WorkflowStep]:
        return self.step.always + (
            self.step.success if self.succeeded else self.step.failure
        )

    def to_json(self):
        return self.__dict__

    def from_json(json_data):
        return StepResult(**json_data)


@dataclass
class Workflow:
    name: str = ""
    steps: list[WorkflowStep] = None

    def __post_init__(self):
        self.step_lookup = {}
        for step in self.steps:
            # Create a lookup for quick access to steps by name
            self.step_lookup[step.name] = step

    def to_json(self):
        return self.__dict__

    def from_json(json_data):
        return Workflow(
            name=json_data.get("name", ""), steps=json_data.get("steps", [])
        )


workflow1 = Workflow(
    name="HelloWorldWorkflow",
    steps=[
        WorkflowStep(name="step1", success=["step2"]),
        WorkflowStep(name="step2", success=["step3", "step4", "step2.2"]),
        WorkflowStep(name="step2.2"),
        WorkflowStep(name="step3", success=["step5"]),
        WorkflowStep(name="step4", success=["step6", "step7"]),
        WorkflowStep(name="step5"),
        WorkflowStep(name="step6"),
        WorkflowStep(name="step7", success=["step8"]),
        WorkflowStep(
            name="step8",
        ),
    ],
)


# An HTTP-triggered function with a Durable Functions client binding
@myApp.route(methods=[HTTPMethod.GET], route="start_workflow")
@myApp.durable_client_input(client_name="client")
async def start_workflow(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    logging.info("Starting run_workflow DF")
    instance_id = await client.start_new("run_workflow", client_input=workflow1)
    response = client.create_check_status_response(req, instance_id)
    return response


# Orchestrator
@myApp.orchestration_trigger(context_name="context")
def run_workflow(context: df.DurableOrchestrationContext):
    workflow: Workflow = context.get_input()

    logging.info(f"Starting execution of workflow: {workflow.name}")

    # Initialize the current step
    pending_steps = [workflow.steps[0]]
    running_tasks: dict[str, Any] = {}
    completed_steps: list[StepResult] = []

    while pending_steps or running_tasks:
        # start all pending steps
        while pending_steps:
            step = pending_steps.pop(0)
            step_name = step.name

            # Start the activity for the step and track it
            logging.info(f"Starting job_orchestrator sub-orch for step: {step_name} {step}")
            task = context.call_sub_orchestrator("job_orchestrator", step.to_json())
            running_tasks[step_name] = task
            logging.info(f"Started job_orchestrator for step: {step_name} {step}")

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
                f"Unexpected result type: {type(step_result_out)}. Expected StepResult. step_result_out: {step_result_out}"
            )
            raise Exception(f"Unexpected result type from task_any. step_result: {step_result_out}")
        
        step_result = StepResult.from_json(step_result_out)

        logging.info(f"Completed step: {step_result.step}")
        completed_steps.append(step_result)
        del running_tasks[step_result.step.name]  # Remove from running tasks

        # Enqueue next steps based on the completed step
        next_steps = step_result.next_steps()

        for next_step_name in next_steps:
            next_step = workflow.step_lookup[next_step_name]
            if next_step and next_step not in pending_steps:
                # Only add to pending if it hasn't been started yet
                logging.info(f"Enqueuing next step: {next_step.name}")
                pending_steps.append(next_step)
            else:
                logging.info(f"Skipping already pending step: {next_step.name}")

    logging.info(
        f"Workflow is done. Completed step names: {[s.step.name for s in completed_steps]}. Step results: {completed_steps}"
    )
    return "Workflow completed"


# Orchestrator
@myApp.orchestration_trigger(context_name="context")
def job_orchestrator(context: df.DurableOrchestrationContext):
    step = WorkflowStep.from_json(context.get_input())

    logging.info(
        f"job_orchestrator: Starting execution for step: {step.name}. "
        f"Step details: {step}"
    )

    result = yield context.call_activity("job_runner_activity", step.to_json())

    logging.info(
        f"job_orchestrator: Received result for step: {step.name}. Result: {result}"
    )

    return result


@myApp.activity_trigger(input_name="input")
def job_runner_activity(input: dict) -> str:
    step = WorkflowStep.from_json(input)
    logging.info(f"Running step: {step.name}")
    time.sleep(2)  # Simulate some processing time
    return StepResult(step=step, succeeded=True).to_json()
