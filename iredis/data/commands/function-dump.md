Return the serialized payload of loaded libraries.
You can restore the serialized payload later with the `FUNCTION RESTORE` command.

For more information please refer to [Introduction to Redis Functions](/topics/functions-intro).

@return

@bulk-string-reply: the serialized payload

@examples

The following example shows how to dump loaded libraries using `FUNCTION DUMP` and then it calls `FUNCTION FLUSH` deletes all the libraries.
Then, it restores the original libraries from the serialized payload with `FUNCTION RESTORE`.

```
redis> FUNCTION DUMP
"\xf6\x05mylib\x03LUA\x00\xc3@D@J\x1aredis.register_function('my@\x0b\x02', @\x06`\x12\x11keys, args) return`\x0c\a[1] end)\n\x00@\n)\x11\xc8|\x9b\xe4"
redis> FUNCTION FLUSH
OK
redis> FUNCTION RESTORE "\xf6\x05mylib\x03LUA\x00\xc3@D@J\x1aredis.register_function('my@\x0b\x02', @\x06`\x12\x11keys, args) return`\x0c\a[1] end)\n\x00@\n)\x11\xc8|\x9b\xe4"
OK
redis> FUNCTION LIST
1) 1) "library_name"
   2) "mylib"
   3) "engine"
   4) "LUA"
   5) "description"
   6) (nil)
   7) "functions"
   8) 1) 1) "name"
         2) "myfunc"
         3) "description"
         4) (nil)
```
