Sets or clears the bit at _offset_ in the string value stored at _key_.

The bit is either set or cleared depending on _value_, which can be either 0 or
1.
When _key_ does not exist, a new string value is created.
The string is grown to make sure it can hold a bit at _offset_.
The _offset_ argument is required to be greater than or equal to 0, and smaller
than 2^32 (this limits bitmaps to 512MB).
When the string at _key_ is grown, added bits are set to 0.

**Warning**: When setting the last possible bit (_offset_ equal to 2^32 -1) and
the string value stored at _key_ does not yet hold a string value, or holds a
small string value, Redis needs to allocate all intermediate memory which can
block the server for some time.
On a 2010 MacBook Pro, setting bit number 2^32 -1 (512MB allocation) takes
~300ms, setting bit number 2^30 -1 (128MB allocation) takes ~80ms, setting bit
number 2^28 -1 (32MB allocation) takes ~30ms and setting bit number 2^26 -1 (8MB
allocation) takes ~8ms.
Note that once this first allocation is done, subsequent calls to `SETBIT` for
the same _key_ will not have the allocation overhead.

@return

@integer-reply: the original bit value stored at _offset_.

@examples

```cli
SETBIT mykey 7 1
SETBIT mykey 7 0
GET mykey
```
