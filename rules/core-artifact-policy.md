# Artifact Policy

Choose storage by the artifact's lifetime, then publish only what should be public.

## Keep disposable and durable work distinct

Use SmartKit's shared artifact cache for disposable temporary files unless the user, project, or applicable Skill specifies another location or lifecycle. Retention is configurable per artifact and defaults to seven days.

An unspecified directory does not make an output disposable. Preserve source edits, canonical records, and sole copies requiring preservation under their owning contracts. Sensitive acquisition material that needs earlier deletion stays in its owner's private storage and deletion lifecycle.

## Use the installed shared tool

Resolve `local_web` from the absolute path in the loaded installation's `SmartKit plugin resources` metadata, independently of the target project's working directory. Before using temporary storage, publishing an artifact, or generating a local diff link, read its command interface:

```bash
python "<local_web>" --help
```

Substitute the supplied path. The unified CLI help owns operation inputs, commands, and results; the full SmartKit plugin and Python 3.8+ are prerequisites.

If required metadata, the tool, or Python capability is unavailable, report the missing prerequisite and leave dependent output incomplete. An arbitrary project directory is not a substitute, and unavailable publication cannot be reported as URL delivery.

## Publish explicitly

Cache privately by default. Creating an artifact neither starts an HTTP service nor returns a URL.

When web display is appropriate and authorized, declare the intended public files and publish the retained artifact through the web tool. Use its returned current URL and leave private files undeclared. Reuse a captured artifact or URL already returned by a feature tool instead of caching or publishing it again.
