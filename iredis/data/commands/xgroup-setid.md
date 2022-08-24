Set the **last delivered ID** for a consumer group.

Normally, a consumer group's last delivered ID is set when the group is created with `XGROUP CREATE`.
The `XGROUP SETID` command allows modifying the group's last delivered ID, without having to delete and recreate the group.
For instance if you want the consumers in a consumer group to re-process all the messages in a stream, you may want to set its next ID to 0:

    XGROUP SETID mystream mygroup 0

The optional `entries_read` argument can be specified to enable consumer group lag tracking for an arbitrary ID.
An arbitrary ID is any ID that isn't the ID of the stream's first entry, its last entry or the zero ("0-0") ID.
This can be useful you know exactly how many entries are between the arbitrary ID (excluding it) and the stream's last entry.
In such cases, the `entries_read` can be set to the stream's `entries_added` subtracted with the number of entries.

@return

@simple-string-reply: `OK` on success.
