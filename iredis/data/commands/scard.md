Returns the set cardinality (number of elements) of the set stored at `key`.

@return

@integer-reply: the cardinality (number of elements) of the set, or `0` if `key`
does not exist.

@examples

```cli
SADD myset "Hello"
SADD myset "World"
SCARD myset
```
