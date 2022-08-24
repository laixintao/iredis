This command copies the value stored at the `source` key to the `destination`
key.

By default, the `destination` key is created in the logical database used by the
connection. The `DB` option allows specifying an alternative logical database
index for the destination key.

The command returns an error when the `destination` key already exists. The
`REPLACE` option removes the `destination` key before copying the value to it.

@return

@integer-reply, specifically:

* `1` if `source` was copied.
* `0` if `source` was not copied.

@examples

```
SET dolly "sheep"
COPY dolly clone
GET clone
```