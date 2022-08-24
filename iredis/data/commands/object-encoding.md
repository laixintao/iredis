Returns the internal encoding for the Redis object stored at `<key>`

Redis objects can be encoded in different ways:

* Strings can be encoded as: 

    - `raw`, normal string encoding.
    - `int`, strings representing integers in a 64-bit signed interval, encoded in this way to save space.
    - `embstr`, an embedded string, which is an object where the internal simple dynamic string, `sds`, is an unmodifiable string allocated in the same chuck as the object itself.
      `embstr` can be strings with lengths up to the hardcoded limit of `OBJ_ENCODING_EMBSTR_SIZE_LIMIT` or 44 bytes. 

* Lists can be encoded as `ziplist` or `linkedlist`. The `ziplist` is the special representation that is used to save space for small lists.
* Sets can be encoded as `intset` or `hashtable`. The `intset` is a special encoding used for small sets composed solely of integers.
* Hashes can be encoded as `ziplist` or `hashtable`. The `ziplist` is a special encoding used for small hashes.
* Sorted Sets can be encoded as `ziplist` or `skiplist` format. As for the List type small sorted sets can be specially encoded using `ziplist`, while the `skiplist` encoding is the one that works with sorted sets of any size.

All the specially encoded types are automatically converted to the general type once you perform an operation that makes it impossible for Redis to retain the space saving encoding.

@return

@bulk-string-reply: the encoding of the object, or `nil` if the key doesn't exist
