Returns @array-reply of details about multiple Redis commands.

Same result format as `COMMAND` except you can specify which commands get
returned.

If you request details about non-existing commands, their return position will
be nil.

@return

@array-reply: nested list of command details.

@examples

```cli
COMMAND INFO get set eval
COMMAND INFO foo evalsha config bar
```
