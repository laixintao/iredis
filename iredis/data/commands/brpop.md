`BRPOP` is a blocking list pop primitive. It is the blocking version of `RPOP`
because it blocks the connection when there are no elements to pop from any of
the given lists. An element is popped from the tail of the first list that is
non-empty, with the given keys being checked in the order that they are given.

See the [BLPOP documentation][cb] for the exact semantics, since `BRPOP` is
identical to `BLPOP` with the only difference being that it pops elements from
the tail of a list instead of popping from the head.

[cb]: /commands/blpop

@return

@array-reply: specifically:

- A `nil` multi-bulk when no element could be popped and the timeout expired.
- A two-element multi-bulk with the first element being the name of the key
  where an element was popped and the second element being the value of the
  popped element.

@examples

```
redis> DEL list1 list2
(integer) 0
redis> RPUSH list1 a b c
(integer) 3
redis> BRPOP list1 list2 0
1) "list1"
2) "c"
```
