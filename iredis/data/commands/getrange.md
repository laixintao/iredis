**Warning**: this command was renamed to `GETRANGE`, it is called `SUBSTR` in
Redis versions `<= 2.0`.

Returns the substring of the string value stored at `key`, determined by the
offsets `start` and `end` (both are inclusive). Negative offsets can be used in
order to provide an offset starting from the end of the string. So -1 means the
last character, -2 the penultimate and so forth.

The function handles out of range requests by limiting the resulting range to
the actual length of the string.

@return

@bulk-string-reply

@examples

```cli
SET mykey "This is a string"
GETRANGE mykey 0 3
GETRANGE mykey -3 -1
GETRANGE mykey 0 -1
GETRANGE mykey 10 100
```
