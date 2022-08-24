Create a consumer named `<consumername>` in the consumer group `<groupname>` of the stream that's stored at `<key>`.

Consumers are also created automatically whenever an operation, such as `XREADGROUP`, references a consumer that doesn't exist.

@return

@integer-reply: the number of created consumers (0 or 1)