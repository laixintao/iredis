Get the value of `key` and delete the key.
This command is similar to `GET`, except for the fact that it also deletes the key on success (if and only if the key's value type is a string).

@return

@bulk-string-reply: the value of `key`, `nil` when `key` does not exist, or an error if the key's value type isn't a string.

@examples

```cli
SET mykey "Hello"
GETDEL mykey
GET mykey
```
