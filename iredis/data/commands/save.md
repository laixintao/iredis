The `SAVE` commands performs a **synchronous** save of the dataset producing a
_point in time_ snapshot of all the data inside the Redis instance, in the form
of an RDB file.

You almost never want to call `SAVE` in production environments where it will
block all the other clients. Instead usually `BGSAVE` is used. However in case
of issues preventing Redis to create the background saving child (for instance
errors in the fork(2) system call), the `SAVE` command can be a good last resort
to perform the dump of the latest dataset.

Please refer to the [persistence documentation][tp] for detailed information.

[tp]: /topics/persistence

@return

@simple-string-reply: The commands returns OK on success.
