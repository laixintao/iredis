This command is exactly like `XRANGE`, but with the notable difference of
returning the entries in reverse order, and also taking the start-end
range in reverse order: in `XREVRANGE` you need to state the *end* ID
and later the *start* ID, and the command will produce all the element
between (or exactly like) the two IDs, starting from the *end* side.

So for instance, to get all the elements from the higher ID to the lower
ID one could use:

    XREVRANGE somestream + -

Similarly to get just the last element added into the stream it is
enough to send:

    XREVRANGE somestream + - COUNT 1

@return

@array-reply, specifically:

The command returns the entries with IDs matching the specified range,
from the higher ID to the lower ID matching.
The returned entries are complete, that means that the ID and all the fields
they are composed are returned. Moreover the entries are returned with
their fields and values in the exact same order as `XADD` added them.

@examples

```cli
XADD writers * name Virginia surname Woolf
XADD writers * name Jane surname Austen
XADD writers * name Toni surname Morrison
XADD writers * name Agatha surname Christie
XADD writers * name Ngozi surname Adichie
XLEN writers
XREVRANGE writers + - COUNT 1
```
