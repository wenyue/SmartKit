# Artifact Policy

## Store Disposable Temporary Artifacts

Use SmartKit's shared artifact cache for disposable temporary files unless the user, project, or applicable Skill specifies their output location or lifecycle. Retention is configurable per artifact and defaults to seven days. An unspecified directory alone does not make an output disposable: preserve source edits, canonical records, and sole copies requiring preservation under their owning contracts. Keep sensitive acquisition material requiring earlier deletion under its owner's private storage and deletion lifecycle.

## Use the Shared Tools

Resolve the shared tool from the `local_web` absolute path in the loaded installation's `SmartKit plugin resources` metadata, independently of the target project's working directory. Before using temporary storage, publishing an artifact, or generating a local diff link, read `python "<local_web>" --help`, substituting its supplied path. The unified CLI help owns the operation inputs, commands, and results. The full SmartKit plugin and Python 3.8+ are required.

If required resource metadata, a tool, or Python capability is unavailable, report the prerequisite gap and leave dependent output incomplete. Do not silently substitute an arbitrary project directory or claim URL delivery.

## Publish Retained Artifacts Explicitly

Cache privately by default; creation alone starts no HTTP service and returns no URL. When web display is appropriate and authorized, explicitly declare the intended public files and publish the retained artifact through the web tool, using its returned current URL. Keep private files undeclared. When a feature tool already returns a captured artifact or URL, reuse that result rather than caching or publishing it again.
