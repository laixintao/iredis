Restore libraries from the serialized payload.

You can use the optional _policy_ argument to provide a policy for handling existing libraries.
The following policies are allowed:

* **APPEND:** appends the restored libraries to the existing libraries and aborts on collision. 
  This is the default policy.
* **FLUSH:** deletes all existing libraries before restoring the payload.
* **REPLACE:** appends the restored libraries to the existing libraries, replacing any existing ones in case of name collisions. Note that this policy doesn't prevent function name collisions, only libraries.

For more information please refer to [Introduction to Redis Functions](/topics/functions-intro).

@return

@simple-string-reply
