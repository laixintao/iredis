Returns the length of the string value stored at `key`. An error is returned
when `key` holds a non-string value.

@return

@integer-reply: the length of the string at `key`, or `0` when `key` does not
exist.

@examples

```cli
SET mykey "Hello world"
STRLEN mykey
STRLEN nonexisting
```
