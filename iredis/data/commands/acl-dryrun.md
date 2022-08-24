Simulate the execution of a given command by a given user.
This command can be used to test the permissions of a given user without having to enable the user or cause the side effects of running the command.

@return

@simple-string-reply: `OK` on success.
@bulk-string-reply: An error describing why the user can't execute the command.

@examples

```
> ACL SETUSER VIRGINIA +SET ~*
"OK"
> ACL DRYRUN VIRGINIA SET foo bar
"OK"
> ACL DRYRUN VIRGINIA GET foo bar
"This user has no permissions to run the 'GET' command"
```
