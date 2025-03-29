# workflow1 - History table

Here's the history for a stuck instance of workflow1. The instance is still in "Running" state.

```
select Timestamp, InstanceID, SequenceNumber, EventType, Name, TaskID, IsPlayed from dt.History where InstanceID = 'fe47ec251173427aa9afa95ed9e93a07';
```

|Timestamp|InstanceID|SequenceNumber|EventType|Name|TaskID|IsPlayed|
|---|---|---|---|---|---|---|
|2025-03-28 07:43:10.1040750|fe47ec251173427aa9afa95ed9e93a07|0|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:09.6255466|fe47ec251173427aa9afa95ed9e93a07|1|ExecutionStarted|workflow_orchestrator|NULL|1|
|2025-03-28 07:43:10.4248370|fe47ec251173427aa9afa95ed9e93a07|2|TaskScheduled|generate_job_id|0|0|
|2025-03-28 07:43:10.4267830|fe47ec251173427aa9afa95ed9e93a07|3|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:11.1231200|fe47ec251173427aa9afa95ed9e93a07|4|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:11.0647334|fe47ec251173427aa9afa95ed9e93a07|5|TaskCompleted|NULL|0|1|
|2025-03-28 07:43:11.1766450|fe47ec251173427aa9afa95ed9e93a07|6|SubOrchestrationInstanceCreated|job_orchestrator|1|0|
|2025-03-28 07:43:11.1811350|fe47ec251173427aa9afa95ed9e93a07|7|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:13.3850240|fe47ec251173427aa9afa95ed9e93a07|8|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:13.3646912|fe47ec251173427aa9afa95ed9e93a07|9|SubOrchestrationInstanceCompleted|NULL|1|1|
|2025-03-28 07:43:13.4097580|fe47ec251173427aa9afa95ed9e93a07|10|TaskScheduled|generate_job_id|2|0|
|2025-03-28 07:43:13.4097720|fe47ec251173427aa9afa95ed9e93a07|11|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:13.4692490|fe47ec251173427aa9afa95ed9e93a07|12|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:13.4544054|fe47ec251173427aa9afa95ed9e93a07|13|TaskCompleted|NULL|2|1|
|2025-03-28 07:43:13.4855180|fe47ec251173427aa9afa95ed9e93a07|14|SubOrchestrationInstanceCreated|job_orchestrator|3|0|
|2025-03-28 07:43:13.4856560|fe47ec251173427aa9afa95ed9e93a07|15|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:15.6630990|fe47ec251173427aa9afa95ed9e93a07|16|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:15.6041444|fe47ec251173427aa9afa95ed9e93a07|17|SubOrchestrationInstanceCompleted|NULL|3|1|
|2025-03-28 07:43:15.6854160|fe47ec251173427aa9afa95ed9e93a07|18|TaskScheduled|generate_job_id|4|0|
|2025-03-28 07:43:15.6854300|fe47ec251173427aa9afa95ed9e93a07|19|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:15.8094800|fe47ec251173427aa9afa95ed9e93a07|20|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:15.7725006|fe47ec251173427aa9afa95ed9e93a07|21|TaskCompleted|NULL|4|1|
|2025-03-28 07:43:15.8432040|fe47ec251173427aa9afa95ed9e93a07|22|TaskScheduled|generate_job_id|5|0|
|2025-03-28 07:43:15.8432210|fe47ec251173427aa9afa95ed9e93a07|23|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:16.1118120|fe47ec251173427aa9afa95ed9e93a07|24|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:16.0402037|fe47ec251173427aa9afa95ed9e93a07|25|TaskCompleted|NULL|5|1|
|2025-03-28 07:43:16.1392420|fe47ec251173427aa9afa95ed9e93a07|26|TaskScheduled|generate_job_id|6|0|
|2025-03-28 07:43:16.1392570|fe47ec251173427aa9afa95ed9e93a07|27|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:16.2708740|fe47ec251173427aa9afa95ed9e93a07|28|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:16.1887072|fe47ec251173427aa9afa95ed9e93a07|29|TaskCompleted|NULL|6|1|
|2025-03-28 07:43:16.3151330|fe47ec251173427aa9afa95ed9e93a07|30|SubOrchestrationInstanceCreated|job_orchestrator|7|0|
|2025-03-28 07:43:16.3151770|fe47ec251173427aa9afa95ed9e93a07|31|SubOrchestrationInstanceCreated|job_orchestrator|8|0|
|2025-03-28 07:43:16.3151830|fe47ec251173427aa9afa95ed9e93a07|32|SubOrchestrationInstanceCreated|job_orchestrator|9|0|
|2025-03-28 07:43:16.3151960|fe47ec251173427aa9afa95ed9e93a07|33|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:18.7825050|fe47ec251173427aa9afa95ed9e93a07|34|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:18.6965453|fe47ec251173427aa9afa95ed9e93a07|35|SubOrchestrationInstanceCompleted|NULL|7|1|
|2025-03-28 07:43:18.8157090|fe47ec251173427aa9afa95ed9e93a07|36|TaskScheduled|generate_job_id|10|0|
|2025-03-28 07:43:18.8157220|fe47ec251173427aa9afa95ed9e93a07|37|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:18.8649720|fe47ec251173427aa9afa95ed9e93a07|38|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:18.7520537|fe47ec251173427aa9afa95ed9e93a07|39|SubOrchestrationInstanceCompleted|NULL|9|1|
|2025-03-28 07:43:18.7684869|fe47ec251173427aa9afa95ed9e93a07|40|SubOrchestrationInstanceCompleted|NULL|8|1|
|2025-03-28 07:43:18.8931420|fe47ec251173427aa9afa95ed9e93a07|41|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:18.9481180|fe47ec251173427aa9afa95ed9e93a07|42|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:18.8517286|fe47ec251173427aa9afa95ed9e93a07|43|TaskCompleted|NULL|10|1|
|2025-03-28 07:43:18.9816660|fe47ec251173427aa9afa95ed9e93a07|44|TaskScheduled|generate_job_id|11|0|
|2025-03-28 07:43:18.9816800|fe47ec251173427aa9afa95ed9e93a07|45|OrchestratorCompleted|NULL|NULL|0|
|2025-03-28 07:43:19.0461730|fe47ec251173427aa9afa95ed9e93a07|46|OrchestratorStarted|NULL|NULL|0|
|2025-03-28 07:43:19.0181399|fe47ec251173427aa9afa95ed9e93a07|47|TaskCompleted|NULL|11|1|
|2025-03-28 07:43:19.0905220|fe47ec251173427aa9afa95ed9e93a07|48|OrchestratorCompleted|NULL|NULL|0|
