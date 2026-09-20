# Comment judgment examples

These contrasting drafts illustrate information selection and voice. The stated context supplies
each example's facts; it is not evidence about a target implementation or user-approved style.
Adapt the judgment to the target's contracts, comment syntax, documentation language, and formatting
requirements. The examples use English for illustration, not as a cross-project requirement.

## Simple interface or component

Context: the parent owns the selected tab. This component displays that selection and reports clicks;
it holds no selection state. Comparable components have short documentation comments.

```ts
/** Supplies the current selection and receives requests to select another tab. */
interface TabStripProps {
  tabs: readonly Tab[];
  selectedId: string;
  onSelect: (id: string) => void;
}
```

The comment explains the parent-facing boundary and distinguishes receiving a request from
changing the selection. Repeating each property name or praising the component's flexibility
would add little. A target requiring individual property documentation would still receive it.

## Complex caller contract

Context: this Go interface crosses a storage boundary, currently with one caller. Its accepted
contract requires atomic batches and permits retry after an uncertain network outcome only by
reusing the same key and entries. Reusing a key with different entries is an error.

```go
type Ledger interface {
    // Apply records all entries atomically. Repeating a key with identical entries
    // returns the original receipt; reusing it with different entries fails.
    // After a timeout, retry with the same key and entries: the first attempt
    // may already have committed.
    Apply(ctx context.Context, key string, entries []Entry) (Receipt, error)
}
```

The contract matters despite having one caller. Atomicity and the timeout consequence guide correct
use beyond the signature. The method-name opening fits Go documentation practice; internal lock or
database details belong with their implementation unless they affect this contract.

## Lifecycle

Context: this TypeScript subscription attaches one listener immediately. The returned function removes
that listener and is safe to call again. The view owner must call it when disposing the view.

```ts
/** Subscribes to ticks until the returned cleanup function is called. */
function subscribeToTicks(onTick: () => void): () => void {
  clock.addEventListener("tick", onTick);
  return () => clock.removeEventListener("tick", onTick);
}

const stopTicks = subscribeToTicks(refresh);
view.onDispose(stopTicks);
```

The comment exposes the lifetime obligation at the callable boundary. The disposal call shows how
this caller fulfills it, so another comment narrating registration or cleanup is unnecessary. If
disposal could leave queued callbacks active, that would need different evidence and wording.

## Local rationale

Context: a Python callback may unsubscribe itself. Iterating the live set would fail if its size
changed; callbacks in the initial snapshot must still receive this dispatch.

```python
# Snapshot the listeners so callbacks can unsubscribe during dispatch.
for listener in tuple(listeners):
    listener(event)
```

The comment explains why the snapshot exists, instead of narrating conversion to a tuple. The
dispatch contract owns the delivery guarantee; this local note need not duplicate it. In a longer
function, a sparse label such as `# Publish notifications` could also help readers find a coherent
section even when it adds no hidden rationale.

## Necessary longer explanation

Context: an append-only log stores checksummed records. The format permits a final incomplete record
after a crash. Its recovery contract rejects complete records with invalid checksums, including at
the end, because that condition indicates corruption rather than a permitted interrupted append.

```rust
// A crash can leave the last record incomplete, so recovery may discard that
// trailing fragment. A complete record with a bad checksum is different: it
// indicates corruption, and discarding it could silently lose committed data.
// Check completeness before validating the checksum so only an interrupted
// append takes the truncation path.
match read_record(input)? {
    RecordRead::IncompleteTail => {
        truncate_to_last_record()?;
        break;
    }
    RecordRead::Complete(record) => {
        verify_checksum(&record)?;
        replay(record)?;
    }
    RecordRead::End => break,
}
```

The relationship between crash recovery, corruption, and ordering earns the space. Compressing it
to “handle partial records” would lose the reason the two paths differ. The excerpt assumes an
enclosing recovery loop; the comment need not retell the format's full specification or its history.

## Deliberate omission

Context: a local Python helper has no additional validation, units, side effects, or caller
obligations. Comparable helpers mix short useful comments with uncommented straightforward code;
no explicit documentation requirement applies.

```python
def is_empty(self) -> bool:
    return not self.items
```

Leave it uncommented. The name and body already supply the useful account, so “returns whether
items is empty” would repeat it. This choice follows the helper's purpose, simplicity, information
value, and local context together; neither nearby absence nor public visibility decides it alone.
