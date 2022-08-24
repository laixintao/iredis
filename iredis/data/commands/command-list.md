Return an array of the server's command names.

You can use the optional _FILTERBY_ modifier to apply one of the following filters:

 - **MODULE module-name**: get the commands that belong to the module specified by _module-name_.
 - **ACLCAT category**: get the commands in the [ACL category](/docs/manual/security/acl/#command-categories) specified by _category_.
 - **PATTERN pattern**: get the commands that match the given glob-like _pattern_.

@return

@array-reply: a list of command names.
