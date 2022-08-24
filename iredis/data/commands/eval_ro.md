This is a read-only variant of the `EVAL` command that cannot execute commands that modify data.

For more information about when to use this command vs `EVAL`, please refer to [Read-only scripts](/docs/manual/programmability/#read-only_scripts).

For more information about `EVAL` scripts please refer to [Introduction to Eval Scripts](/topics/eval-intro).

@examples

```
> SET mykey "Hello"
OK

> EVAL_RO "return redis.call('GET', KEYS[1])" 1 mykey
"Hello"

> EVAL_RO "return redis.call('DEL', KEYS[1])" 1 mykey
(error) ERR Error running script (call to b0d697da25b13e49157b2c214a4033546aba2104): @user_script:1: @user_script: 1: Write commands are not allowed from read-only scripts.
```
