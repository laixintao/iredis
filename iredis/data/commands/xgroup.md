This command is used in order to manage the consumer groups associated with a
stream data structure. Using `XGROUP` you can:

- Create a new consumer group associated with a stream.
- Destroy a consumer group.
- Remove a specific consumer from a consumer group.
- Set the consumer group _last delivered ID_ to something else.

To create a new consumer group, use the following form:

    XGROUP CREATE mystream consumer-group-name $

The last argument is the ID of the last item in the stream to consider already
delivered. In the above case we used the special ID '\$' (that means: the ID of
the last item in the stream). In this case the consumers fetching data from that
consumer group will only see new elements arriving in the stream.

If instead you want consumers to fetch the whole stream history, use zero as the
starting ID for the consumer group:

    XGROUP CREATE mystream consumer-group-name 0

Of course it is also possible to use any other valid ID. If the specified
consumer group already exists, the command returns a `-BUSYGROUP` error.
Otherwise the operation is performed and OK is returned. There are no hard
limits to the number of consumer groups you can associate to a given stream.

If the specified stream doesn't exist when creating a group, an error will be
returned. You can use the optional `MKSTREAM` subcommand as the last argument
after the `ID` to automatically create the stream, if it doesn't exist. Note
that if the stream is created in this way it will have a length of 0:

    XGROUP CREATE mystream consumer-group-name $ MKSTREAM

A consumer group can be destroyed completely by using the following form:

    XGROUP DESTROY mystream consumer-group-name

The consumer group will be destroyed even if there are active consumers and
pending messages, so make sure to call this command only when really needed.

To just remove a given consumer from a consumer group, the following form is
used:

    XGROUP DELCONSUMER mystream consumer-group-name myconsumer123

Consumers in a consumer group are auto-created every time a new consumer name is
mentioned by some command. However sometimes it may be useful to remove old
consumers since they are no longer used. This form returns the number of pending
messages that the consumer had before it was deleted.

Finally it possible to set the next message to deliver using the `SETID`
subcommand. Normally the next ID is set when the consumer is created, as the
last argument of `XGROUP CREATE`. However using this form the next ID can be
modified later without deleting and creating the consumer group again. For
instance if you want the consumers in a consumer group to re-process all the
messages in a stream, you may want to set its next ID to 0:

    XGROUP SETID mystream consumer-group-name 0

Finally to get some help if you don't remember the syntax, use the HELP
subcommand:

    XGROUP HELP
