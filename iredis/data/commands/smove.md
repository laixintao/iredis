Move `member` from the set at `source` to the set at `destination`. This
operation is atomic. In every given moment the element will appear to be a
member of `source` **or** `destination` for other clients.

If the source set does not exist or does not contain the specified element, no
operation is performed and `0` is returned. Otherwise, the element is removed
from the source set and added to the destination set. When the specified element
already exists in the destination set, it is only removed from the source set.

An error is returned if `source` or `destination` does not hold a set value.

@return

@integer-reply, specifically:

- `1` if the element is moved.
- `0` if the element is not a member of `source` and no operation was performed.

@examples

```cli
SADD myset "one"
SADD myset "two"
SADD myotherset "three"
SMOVE myset myotherset "two"
SMEMBERS myset
SMEMBERS myotherset
```
