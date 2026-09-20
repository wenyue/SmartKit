# Generated Files

**Strength:** Mandatory
**Scope:** Changes affecting generated files in repositories that adopt this Rule.

Maintain generated files through their canonical sources and owning generator. Establish that
ownership from the repository's configuration or documentation before editing. When a source,
generator, or configured input changes the expected output, regenerate the affected files using
the repository's declared tool and settings. Hand edits to generated output cannot substitute for
generation.

Review the generated differences against the authorized change. Resolve unrelated output changes
before retaining them, and preserve existing work. The change is complete when the affected
sources and outputs agree under the repository's verification method and every required generated
file is included with its source change.

If ownership, the generation method, required tools, verification, or permission is missing, stop
dependent work and identify the prerequisite. If generation or verification fails, report the
failure and any resulting file changes; completion remains blocked until agreement is verified.

The repository owns the sources, tool configuration, and verification requirements. This Rule
governs their consistency within the authorized task; it grants no additional write, installation,
or network authority.
