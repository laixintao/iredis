The LOLWUT command displays the Redis version: however as a side effect of doing
so, it also creates a piece of generative computer art that is different with
each version of Redis. The command was introduced in Redis 5 and announced with
this [blog post](http://antirez.com/news/123).

By default the `LOLWUT` command will display the piece corresponding to the
current Redis version, however it is possible to display a specific version
using the following form:

    LOLWUT VERSION 5 ... other optional arguments ...

Of course the "5" above is an example. Each LOLWUT version takes a different set
of arguments in order to change the output. The user is encouraged to play with
it to discover how the output changes adding more numerical arguments.

LOLWUT wants to be a reminder that there is more in programming than just
putting some code together in order to create something useful. Every LOLWUT
version should have the following properties:

1. It should display some computer art. There are no limits as long as the
   output works well in a normal terminal display. However the output should not
   be limited to graphics (like LOLWUT 5 and 6 actually do), but can be
   generative poetry and other non graphical things.
2. LOLWUT output should be completely useless. Displaying some useful Redis
   internal metrics does not count as a valid LOLWUT.
3. LOLWUT output should be fast to generate so that the command can be called in
   production instances without issues. It should remain fast even when the user
   experiments with odd parameters.
4. LOLWUT implementations should be safe and carefully checked for security, and
   resist to untrusted inputs if they take arguments.
5. LOLWUT must always display the Redis version at the end.

@return

@bulk-string-reply (or verbatim reply when using the RESP3 protocol): the string
containing the generative computer art, and a text with the Redis version.
