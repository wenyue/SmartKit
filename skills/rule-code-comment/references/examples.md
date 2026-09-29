# Comment judgment examples

These contrasting drafts illustrate information selection and voice. The stated context supplies
each example's facts; it is not evidence about a target implementation or user-approved style.
Adapt the judgment to the target's contracts, comment syntax, documentation language, and formatting
requirements. The examples use English for illustration, not as a cross-project requirement.
Snippets omit imports and surrounding declarations; their contexts establish the relevant contracts.

## Simple interface or component

Context: the parent owns the selected tab. This component displays that selection and reports clicks;
it holds no selection state. Comparable components have short documentation comments.

```dart
/// Supplies the current selection and receives requests to select another tab.
class TabStripProps {
  const TabStripProps(this.tabs, this.selectedId, this.onSelect);

  final List<Tab> tabs;
  final String selectedId;
  final void Function(String) onSelect;
}
```

The comment explains the parent-facing boundary and distinguishes receiving a request from
changing the selection. Repeating each property name or praising the component's flexibility
would add little. A target requiring individual property documentation would still receive it.

## Complex caller contract

Context: this interface crosses a storage boundary, currently with one caller. Its accepted
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
use beyond the signature. The method-name opening fits local documentation practice; internal lock
or database details belong with their implementation unless they affect this contract.

## Failure as part of the caller contract

These examples document established failure contracts. Their comments tell callers what failed,
how to recognize it, and what state remains; they do not choose a new error design.

### Thrown and intentionally propagated failures

Context: this method belongs to a read-only configuration reader whose `file` is a `File`. Its
accepted contract requires a UTF-8 JSON object. Callers distinguish invalid content from failed
access using the existing `FormatException` and `FileSystemException` categories. The reader
neither repairs the file nor saves defaults.

```dart
/// Loads configuration from a UTF-8 JSON object.
///
/// Throws [FormatException] for invalid UTF-8, invalid JSON, or a non-object root.
/// Propagates [FileSystemException] when the file cannot be read.
/// Failure leaves stored bytes untouched; no defaults are written.
Map<String, dynamic> load() {
  final value = jsonDecode(utf8.decode(file.readAsBytesSync()));
  if (value is! Map<String, dynamic>) {
    throw const FormatException('Expected a JSON object');
  }
  return value;
}
```

The categories let callers distinguish a content correction from an access problem. The read
failure belongs in the comment even though this method intentionally lets it propagate. The
remaining-state statement prevents callers from assuming that failure repaired or replaced the
configuration. Naming decoder internals or listing incidental runtime failures would not help
these caller decisions.

### Returned failures with stable recognition

Context: this resource API reads from a filesystem without changing stored content. Its accepted
contract preserves the filesystem's error identities, including `fs.ErrNotExist` for a missing
resource, and returns no data on failure even if the underlying read produced some bytes.

```go
// LoadResource reads name without modifying stored content.
// If name is absent, errors.Is(err, fs.ErrNotExist) is true.
// Other read errors retain their identities. On error, data is nil.
func LoadResource(fsys fs.FS, name string) ([]byte, error) {
	data, err := fs.ReadFile(fsys, name)
	if err != nil {
		return nil, fmt.Errorf("load resource %q: %w", name, err)
	}
	return data, nil
}
```

The missing-resource condition and matching operation let callers decide whether to choose another
resource. Other read failures propagate with context and retain the already-promised recognition.
The no-data promise prevents a partial read from being mistaken for a usable result, while the
read-only promise makes the remaining stored state clear. Listing filesystem implementation details
or individual error-message strings would add no stable caller contract.

## Lifecycle

Context: this helper subscribes to a tick stream. The source may need asynchronous cleanup. The
owner's `onClose` hook accepts cleanup callbacks returning `Future<void>`, awaits them, and surfaces
cleanup failures. The registration lines run inside the owner's setup method.

```dart
/// Delivers ticks until the caller cancels the returned subscription.
/// Cancellation stops delivery immediately; await it to finish source cleanup.
StreamSubscription<int> subscribeToTicks(
  Stream<int> ticks,
  void Function(int) onTick,
) {
  return ticks.listen(onTick);
}

final subscription = subscribeToTicks(ticks, refresh);
owner.onClose(subscription.cancel);
```

The comment exposes the caller's lifetime obligation and distinguishes stopping events from
finishing cleanup. The registered cancellation method returns its future to the established owner,
so cleanup completion and failure remain observable. Another comment narrating registration would
add little. A lifecycle hook that cannot await cleanup would require a different ownership account.

## Local rationale

Context: a callback may unsubscribe itself from the mutable listener set. Iterating the live set
would fail if its size changed; callbacks in the initial snapshot must still receive this dispatch.

```dart
// Snapshot the listeners so callbacks can unsubscribe during dispatch.
for (final listener in listeners.toList()) {
  listener(event);
}
```

The comment explains why the snapshot exists, instead of narrating conversion to a list. The
dispatch contract owns the delivery guarantee; this local note need not duplicate it. In a longer
function, a sparse label such as `// Publish notifications` could also help readers find a coherent
section even when it adds no hidden rationale.

## Necessary longer explanation

Context: an append-only log stores checksummed records. Its recovery contract permits discarding a
final incomplete record after a crash and rejects complete records with invalid checksums, including
at the end. The reader returns `io.EOF` only between records and `io.ErrUnexpectedEOF` only for an
incomplete final record. The fragment runs inside a recovery method returning `error`;
`truncateToLastRecord` removes only that incomplete tail, and the other helpers do not truncate.

```go
// A crash can leave the last record incomplete, so recovery may discard that
// trailing fragment. A complete record with a bad checksum is different: it
// indicates corruption, and discarding it could silently lose committed data.
// Check completeness before validating the checksum so only an interrupted
// append takes the truncation path.
for {
	record, err := readRecord(input)
	if errors.Is(err, io.EOF) {
		return nil
	}
	if errors.Is(err, io.ErrUnexpectedEOF) {
		if err := truncateToLastRecord(); err != nil {
			return fmt.Errorf("discard incomplete log tail: %w", err)
		}
		return nil
	}
	if err != nil {
		return fmt.Errorf("read log record: %w", err)
	}
	if err := verifyChecksum(record); err != nil {
		return fmt.Errorf("verify log record checksum: %w", err)
	}
	if err := replay(record); err != nil {
		return fmt.Errorf("replay log record: %w", err)
	}
}
```

The relationship between crash recovery, corruption, and ordering earns the space. Compressing it
to “handle partial records” would lose the reason the two paths differ. The failure returns keep
read, checksum, replay, and truncation failures visible without treating them all as permission to
truncate. The comment need not retell the format's full specification or its history.

## Deliberate omission

Context: a local collection wrapper has no additional validation, units, side effects, or caller
obligations. Comparable helpers mix short useful comments with uncommented straightforward code;
no explicit documentation requirement applies.

```dart
bool get isEmpty => items.isEmpty;
```

Leave it uncommented. The name and body already supply the useful account, so “returns whether
items is empty” would repeat it. This choice follows the helper's purpose, simplicity, information
value, and local context together; neither nearby absence nor public visibility decides it alone.
