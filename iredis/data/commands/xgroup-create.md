Create a new consumer group uniquely identified by `<groupname>` for the stream stored at `<key>`

Every group has a unique name in a given stream. 
When a consumer group with the same name already exists, the command returns a `-BUSYGROUP` error.

The command's `<id>` argument specifies the last delivered entry in the stream from the new group's perspective.
The special ID `$` is the ID of the last entry in the stream, but you can substitute it with any valid ID.

For example, if you want the group's consumers to fetch the entire stream from the beginning, use zero as the starting ID for the consumer group:

    XGROUP CREATE mystream mygroup 0

By default, the `XGROUP CREATE` command expects that the target stream exists, and returns an error when it doesn't.
If a stream does not exist, you can create it automatically with length of 0 by using the optional `MKSTREAM` subcommand as the last argument after the `<id>`:

    XGROUP CREATE mystream mygroup $ MKSTREAM

To enable consumer group lag tracking, specify the optional `entries_read` named argument with an arbitrary ID.
An arbitrary ID is any ID that isn't the ID of the stream's first entry, last entry, or zero ("0-0") ID.
Use it to find out how many entries are between the arbitrary ID (excluding it) and the stream's last entry.
Set the `entries_read` the stream's `entries_added` subtracted by the number of entries.

@return

@simple-string-reply: `OK` on success.
