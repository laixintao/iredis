This command returns the list of consumers that belong to the `<groupname>` consumer group of the stream stored at `<key>`.

The following information is provided for each consumer in the group:

* **name**: the consumer's name
* **pending**: the number of pending messages for the client, which are messages that were delivered but are yet to be acknowledged
* **idle**: the number of milliseconds that have passed since the consumer last interacted with the server

@reply

@array-reply: a list of consumers.

@examples

```
> XINFO CONSUMERS mystream mygroup
1) 1) name
   2) "Alice"
   3) pending
   4) (integer) 1
   5) idle
   6) (integer) 9104628
2) 1) name
   2) "Bob"
   3) pending
   4) (integer) 1
   5) idle
   6) (integer) 83841983
```
