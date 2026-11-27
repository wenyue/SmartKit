# Comment judgment examples

Each case supplies its own facts. Use the examples to judge what a reader needs and where they will look for it. Their snippets illustrate possible wording in English. The target project supplies its own contracts, language, and format.

## A decision that survives a move

The user accepted cached titles in a preview list so opening the list requires no network request. Cached titles can be up to one minute old. Opening an individual item fetches its current title. A maintainer looking at the list code could reasonably conclude that it is missing a refresh.

```dart
// Use cached titles so opening the list needs no network request. Titles may
// be up to one minute old. Opening an item fetches its current title.
final previews = previewCache.readWithin(const Duration(minutes: 1));
```

Suppose a refactor gives a preview repository responsibility for choosing how to load preview titles. That repository now owns the decision a maintainer could undo by adding a network request. Carry the reason and freshness bound there. If clients choose between preview and detail APIs based on freshness, document the observable difference at those APIs. The old list comment can go once the explanations are available to their readers.

In review, a title that is forty seconds old fits the accepted behavior. Serving a cached list title for longer than a minute exceeds the accepted bound. Opening an item without fetching its current title would violate the separate detail contract. The prior decision helps evaluate these observations without turning either into a blanket claim about caching.

## What callers need before a retry

A ledger commits each batch atomically. A timeout can occur after the commit. A retry with the same key and entries commits the batch if the first attempt did not commit. If it did commit, the retry returns the existing receipt. Reusing a committed key with different entries fails. Even with only one caller, the signature leaves a consequential retry choice open.

```go
// Apply records the batch atomically. A timeout can leave the commit outcome
// unknown. Retry with the same key and entries. If the batch already
// committed, the retry returns its receipt without applying it again.
// Reusing a committed key with different entries fails.
Apply(ctx context.Context, key string, entries []Entry) (Receipt, error)
```

The documentation belongs on the interface where the caller chooses the retry key. Naming the lock or transaction primitive would tie it to implementation details without answering that question.

## Two ways callers recognize failure

A read-only Dart configuration reader accepts UTF-8 JSON objects. Its callers can correct invalid content or handle a filesystem access problem. They also need to know whether a failed load wrote defaults.

```dart
/// Loads the configuration from a UTF-8 JSON object.
///
/// Throws [FormatException] for invalid UTF-8, invalid JSON, or a non-object
/// root. Propagates [FileSystemException] when the file cannot be read.
/// On failure the stored bytes are unchanged.
Map<String, dynamic> load() {
  final value = jsonDecode(utf8.decode(file.readAsBytesSync()));
  if (value is! Map<String, dynamic>) {
    throw const FormatException('Expected a JSON object');
  }
  return value;
}
```

A Go resource loader instead returns a wrapped filesystem error and discards partial data. Its contract preserves filesystem error identities so callers can use the native matching operation.

```go
// LoadResource reads name without changing stored content. For a missing
// resource, errors.Is(err, fs.ErrNotExist) is true. Other read errors retain
// their identities. Every failure returns nil data.
func LoadResource(fsys fs.FS, name string) ([]byte, error) {
	data, err := fs.ReadFile(fsys, name)
	if err != nil {
		return nil, fmt.Errorf("load resource %q: %w", name, err)
	}
	return data, nil
}
```

Both callers get the condition, the recognition their API promises, and the relevant state after failure. Neither depends on matching an incidental error message.

## A caller obligation and a local implementation reason

A stream subscription can stop delivering events before its source finishes cleaning up. The person cancelling it needs to know when resources are free.

```dart
/// Delivers ticks until the caller cancels the returned subscription.
/// Cancellation stops delivery immediately. Await it to finish source cleanup.
StreamSubscription<int> subscribeToTicks(
  Stream<int> ticks,
  void Function(int) onTick,
) {
  return ticks.listen(onTick);
}
```

A caller can now pass the cancellation method to a shutdown hook that awaits its result. The documentation of the subscription explains the caller's obligation without assuming that every caller uses the same hook.

In a different dispatcher, a listener may unsubscribe itself while receiving an event. A future maintainer might remove the snapshot as an unnecessary allocation. The reason belongs on the line where they would make that change.

```dart
// Snapshot the listeners so callbacks can unsubscribe during dispatch.
for (final listener in listeners.toList()) {
  listener(event);
}
```

## How much explanation earns its place

A component displays a selected tab and reports clicks to its parent. Its properties already identify the selected tab and the callback. A short interface comment can explain the ownership boundary in one sentence.

```dart
/// Supplies the parent’s selected tab and receives requests to change it.
class TabStripProps {
  const TabStripProps(this.selectedId, this.onSelect);

  final String selectedId;
  final void Function(String) onSelect;
}
```

A local collection wrapper with no extra validation, units, side effects, or obligations may need even less. Where no explicit coverage requirement applies, the declaration can stand on its own.

```dart
bool get isEmpty => items.isEmpty;
```

By contrast, a recovery routine may truncate an incomplete final log record after a crash. A complete record with a bad checksum indicates corruption, even at the end of the log. Treating both cases as an interrupted append could silently discard committed data. Beside the code that decides whether to truncate, the relationship earns several sentences.

```go
// A crash can leave the final record incomplete. Only that trailing fragment
// may be discarded. Check completeness before validating the checksum so a
// corrupt but complete record is reported without truncating committed data.
```
