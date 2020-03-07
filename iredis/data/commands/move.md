Move `key` from the currently selected database (see `SELECT`) to the specified
destination database. When `key` already exists in the destination database, or
it does not exist in the source database, it does nothing. It is possible to use
`MOVE` as a locking primitive because of this.

@return

@integer-reply, specifically:

- `1` if `key` was moved.
- `0` if `key` was not moved.
