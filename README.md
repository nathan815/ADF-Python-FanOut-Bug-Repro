# ADF Bugs Repro

## How to run this

1. Start mssql and azurite: `docker compose up -d`. 

Wait until `docker compose ps` shows healthy for mssql.

2. Create virtual env:
```
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

3. Start app with core tools: `func start`

4. Start workflow:

GET http://localhost:7071/api/workflows/workflow1

GET http://localhost:7071/api/workflows/workflow2


## Notes

We execute a graph (DAG) of tasks using Durable Functions.

We're using the SQL Server backend. We found that these issues also occur with the default Azure Storage backend.

The workflows are executed by the `workflow_orchestrator` orchestrator function, which manages the execution of steps based on their dependencies. Each step is executed by `job_orchestrator` which in turn calls an activity `job_runner_activity`.

The workflows are defined in YAML in our system. For simplicity I've converted the YAML to python dicts inline in function_app.py.

workflow1 is a mock workflow I made for this.

workflow2 is a real workflow that we have, except I changed the step names to single letters.

workflow3 is a more linear workflow. It does not hit either of the bugs described below.

### New Finding
If I remove the call to start the "generate_job_id" activity, the orchestration does not hit the bugs. It seems the trigger sequence for the bugs in the ADF SDK is:
1. Run an activity
2. Start a sub-orchestation
3. Append sub-orchestration task to `running_tasks`.
4. Call `context.task_any(running_tasks)` 💥

`task_any` is where the AttributeError append error happens. This might also be a hint into why the ADF SDK is getting stuck.

## workflow1

The orchestration just gets stuck after enqueuing step6 and step7. No logs show up after below.

Condition that seems to cause this:

Sibling nodes which each point to 1 or more nodes under them. This creates parallel chains of tasks.

In other words: Two "fan-out" branches which in turn each lead to more tasks starting after they finish.

### SQL Instances table
History table: See [workflow1_history_table.md](./workflow1_history_table.md). It looks like all the tasks were marked as completed, so still no idea where it is getting stuck.

In the Instances table, the "workflow_orchestrator" orchestration is running, but none of the "job_orchestrator" sub-orchestrations are running:

<img width="1008" alt="image" src="https://github.com/user-attachments/assets/32cd3559-4f70-4044-b311-b9bea57d2a09" />


### Logs for workflow1

```
...
[2025-03-28T06:31:21.251Z] Completed step: {'name': 'step3', 'success': ['step5']}
[2025-03-28T06:31:21.252Z] Enqueuing next step: step5
[2025-03-28T06:31:21.252Z] Starting job_orchestrator sub-orch for step: step5 {'name': 'step5'}
[2025-03-28T06:31:21.252Z] Started job_orchestrator for step: step5 {'name': 'step5'}
[2025-03-28T06:31:21.252Z] Waiting for one of these tasks to complete: {'step4': <azure.durable_functions.models.Task.AtomicTask object at 0x109b180d0>, 'step2.2': <azure.durable_functions.models.Task.AtomicTask object at 0x109191790>, 'step5': <azure.durable_functions.models.Task.AtomicTask object at 0x109b1ac90>}
[2025-03-28T06:31:21.252Z] task_any returned task: <azure.durable_functions.models.Task.AtomicTask object at 0x109b180d0>
[2025-03-28T06:31:21.252Z] Completed step: {'name': 'step4', 'success': ['step6', 'step7']}
[2025-03-28T06:31:21.253Z] Enqueuing next step: step6
[2025-03-28T06:31:21.253Z] Enqueuing next step: step7
[2025-03-28T06:31:21.254Z] Executed 'Functions.workflow_orchestrator' (Succeeded, Id=24126292-7cfe-4112-909f-4656b15adbdf, Duration=29ms)
```


## workflow2

This workflow also gets stuck like workflow1, however it hits another bug first. After applying the code workaround in the library code locally, this workflow then runs into the same "stuck" issue as workflow1.

Bug:

It hits an AttributeError in `context.task_any`. Method `_add_to_open_tasks` is calling append on an `AtomicTask` object, which does not have an `append` method. It expects it to be a list.

"Orchestrator function 'workflow_orchestrator' failed: 'AtomicTask' object has no attribute 'append'."

GitHub issue for this: https://github.com/Azure/azure-functions-durable-python/issues/536


### Logs for workflow2

```
...
[2025-03-28T06:55:48.685Z] Completed step: {'name': 'E', 'success': ['G', 'H', 'I']}
[2025-03-28T06:55:48.686Z] Enqueuing next step: G
[2025-03-28T06:55:48.686Z] Enqueuing next step: H
[2025-03-28T06:55:48.687Z] Enqueuing next step: I
[2025-03-28T06:55:48.687Z] Starting job_orchestrator sub-orch for step: G {'name': 'G', 'success': ['J'], 'failure': ['Z']}
[2025-03-28T06:55:48.687Z] Started job_orchestrator for step: G {'name': 'G', 'success': ['J'], 'failure': ['Z']}
[2025-03-28T06:55:48.687Z] Starting job_orchestrator sub-orch for step: H {'name': 'H', 'failure': ['Z']}
[2025-03-28T06:55:48.687Z] Started job_orchestrator for step: H {'name': 'H', 'failure': ['Z']}
[2025-03-28T06:55:48.688Z] Starting job_orchestrator sub-orch for step: I {'name': 'I', 'failure': ['Z']}
[2025-03-28T06:55:48.688Z] Started job_orchestrator for step: I {'name': 'I', 'failure': ['Z']}
[2025-03-28T06:55:48.688Z] Waiting for one of these tasks to complete: {'B': <azure.durable_functions.models.Task.AtomicTask object at 0x111b01a90>, 'F': <azure.durable_functions.models.Task.AtomicTask object at 0x111acecd0>, 'G': <azure.durable_functions.models.Task.AtomicTask object at 0x111ae4350>, 'H': <azure.durable_functions.models.Task.AtomicTask object at 0x111b0f050>, 'I': <azure.durable_functions.models.Task.AtomicTask object at 0x111b0c790>}
[2025-03-28T06:55:48.688Z] task_any returned task: <azure.durable_functions.models.Task.AtomicTask object at 0x111b01a90>
[2025-03-28T06:55:48.688Z] Completed step: {'name': 'B', 'failure': ['Z']}
[2025-03-28T06:55:48.688Z] Waiting for one of these tasks to complete: {'F': <azure.durable_functions.models.Task.AtomicTask object at 0x111acecd0>, 'G': <azure.durable_functions.models.Task.AtomicTask object at 0x111ae4350>, 'H': <azure.durable_functions.models.Task.AtomicTask object at 0x111b0f050>, 'I': <azure.durable_functions.models.Task.AtomicTask object at 0x111b0c790>}
[2025-03-28T06:55:48.689Z] task_any returned task: <azure.durable_functions.models.Task.AtomicTask object at 0x111acecd0>
[2025-03-28T06:55:48.689Z] Completed step: {'name': 'F', 'failure': ['Z']}
[2025-03-28T06:55:48.689Z] Waiting for one of these tasks to complete: {'G': <azure.durable_functions.models.Task.AtomicTask object at 0x111ae4350>, 'H': <azure.durable_functions.models.Task.AtomicTask object at 0x111b0f050>, 'I': <azure.durable_functions.models.Task.AtomicTask object at 0x111b0c790>}
[2025-03-28T06:55:48.695Z] Executed 'Functions.workflow_orchestrator' (Failed, Id=0c15ef3b-6c58-4eda-b8d2-6a1d1c7710a3, Duration=36ms)
[2025-03-28T06:55:48.695Z] System.Private.CoreLib: Exception while executing function: Functions.workflow_orchestrator. Microsoft.Azure.WebJobs.Extensions.DurableTask: Orchestrator function 'workflow_orchestrator' failed: 'AtomicTask' object has no attribute 'append'.
```

### workflow3

Mostly linear until it branches out near the end. No issues with this one.
