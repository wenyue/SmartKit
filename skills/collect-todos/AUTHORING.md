# Authoring Decisions

## Verify records individually

Keep duplicate matching, write reconciliation, and authoritative readback in the capture workflow. A multi-task request can succeed only partly, and an uncertain write can already have created a record. Treating command completion as persistence or retrying the batch blindly would lose task state or create duplicates.

## Keep capture separate from readiness

Recording a prerequisite for later does not remove its blocking effect on the main task. Preserve that distinction so a lightweight capture workflow cannot accidentally turn deferred necessary work into a claim of readiness or completion.
