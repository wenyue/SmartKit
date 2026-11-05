# Artifact Policy

Choose storage by its owner and lifetime, then publish only what should be public.

## Keep disposable and durable work distinct

Keep writable task scratch in temporary storage managed by the task, project, or operating system, with a defined cleanup owner. Keep package, download, and build caches in their tools' storage and lifecycle.

Capture selected disposable output or evidence in SmartKit's shared artifact cache, unless the user, project, or applicable Skill specifies another location or lifecycle. Create each immutable file group through the installed tool, which enforces byte and file-count limits documented in its help. Leave captured contents and directory structure unchanged, and capture a new group for changed or additional files. Retention is configurable per artifact and defaults to seven days.

An unspecified directory does not make an output disposable. Preserve source edits, canonical records, and sole copies requiring preservation under their owning contracts. Sensitive acquisition material that needs earlier deletion stays in its owner's private storage and deletion lifecycle.

## Use the installed shared tool

Resolve `local_web` from the absolute path in the loaded installation's `SmartKit plugin resources` metadata, independently of the target project's working directory. Before capturing files, publishing an artifact, or generating a local diff link, read its command interface.

```bash
python "<local_web>" --help
```

Substitute the supplied path. The unified CLI help owns operation inputs, commands, and results. The full SmartKit plugin and Python 3.8+ are prerequisites.

If required metadata, the tool, or Python capability is unavailable, report the missing prerequisite. Keep dependent output incomplete until the supported installed route succeeds. For retained artifacts, report URL delivery only after successful publication.

## Publish explicitly

Cache privately by default. Creating an artifact neither starts an HTTP service nor returns a URL.

When web display is appropriate and authorized, declare the intended public files and publish the retained artifact through the web tool. Use its returned current URL and leave private files undeclared. Reuse a captured artifact or URL already returned by a feature tool instead of caching or publishing it again.
