Atomically returns and removes the first/last element (head/tail depending on
the `wherefrom` argument) of the list stored at `source`, and pushes the
element at the first/last element (head/tail depending on the `whereto`
argument) of the list stored at `destination`.

For example: consider `source` holding the list `a,b,c`, and `destination`
holding the list `x,y,z`.
Executing `LMOVE source destination RIGHT LEFT` results in `source` holding
`a,b` and `destination` holding `c,x,y,z`.

If `source` does not exist, the value `nil` is returned and no operation is
performed.
If `source` and `destination` are the same, the operation is equivalent to
removing the first/last element from the list and pushing it as first/last
element of the list, so it can be considered as a list rotation command (or a
no-op if `wherefrom` is the same as `whereto`).

This command comes in place of the now deprecated `RPOPLPUSH`. Doing
`LMOVE RIGHT LEFT` is equivalent.

@return

@bulk-string-reply: the element being popped and pushed.

@examples

```cli
RPUSH mylist "one"
RPUSH mylist "two"
RPUSH mylist "three"
LMOVE mylist myotherlist RIGHT LEFT
LMOVE mylist myotherlist LEFT RIGHT
LRANGE mylist 0 -1
LRANGE myotherlist 0 -1
```

## Pattern: Reliable queue

Redis is often used as a messaging server to implement processing of background
jobs or other kinds of messaging tasks.
A simple form of queue is often obtained pushing values into a list in the
producer side, and waiting for this values in the consumer side using `RPOP`
(using polling), or `BRPOP` if the client is better served by a blocking
operation.

However in this context the obtained queue is not _reliable_ as messages can
be lost, for example in the case there is a network problem or if the consumer
crashes just after the message is received but it is still to process.

`LMOVE` (or `BLMOVE` for the blocking variant) offers a way to avoid
this problem: the consumer fetches the message and at the same time pushes it
into a _processing_ list.
It will use the `LREM` command in order to remove the message from the
_processing_ list once the message has been processed.

An additional client may monitor the _processing_ list for items that remain
there for too much time, and will push those timed out items into the queue
again if needed.

## Pattern: Circular list

Using `LMOVE` with the same source and destination key, a client can visit
all the elements of an N-elements list, one after the other, in O(N) without
transferring the full list from the server to the client using a single `LRANGE`
operation.

The above pattern works even if the following two conditions:

* There are multiple clients rotating the list: they'll fetch different
  elements, until all the elements of the list are visited, and the process
  restarts.
* Even if other clients are actively pushing new items at the end of the list.

The above makes it very simple to implement a system where a set of items must
be processed by N workers continuously as fast as possible.
An example is a monitoring system that must check that a set of web sites are
reachable, with the smallest delay possible, using a number of parallel workers.

Note that this implementation of workers is trivially scalable and reliable,
because even if a message is lost the item is still in the queue and will be
processed at the next iteration.
