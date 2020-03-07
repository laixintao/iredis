Return the position of the first bit set to 1 or 0 in a string.

The position is returned, thinking of the string as an array of bits from left
to right, where the first byte's most significant bit is at position 0, the
second byte's most significant bit is at position 8, and so forth.

The same bit position convention is followed by `GETBIT` and `SETBIT`.

By default, all the bytes contained in the string are examined. It is possible
to look for bits only in a specified interval passing the additional arguments
_start_ and _end_ (it is possible to just pass _start_, the operation will
assume that the end is the last byte of the string. However there are semantic
differences as explained later). The range is interpreted as a range of bytes
and not a range of bits, so `start=0` and `end=2` means to look at the first
three bytes.

Note that bit positions are returned always as absolute values starting from bit
zero even when _start_ and _end_ are used to specify a range.

Like for the `GETRANGE` command start and end can contain negative values in
order to index bytes starting from the end of the string, where -1 is the last
byte, -2 is the penultimate, and so forth.

Non-existent keys are treated as empty strings.

@return

@integer-reply

The command returns the position of the first bit set to 1 or 0 according to the
request.

If we look for set bits (the bit argument is 1) and the string is empty or
composed of just zero bytes, -1 is returned.

If we look for clear bits (the bit argument is 0) and the string only contains
bit set to 1, the function returns the first bit not part of the string on the
right. So if the string is three bytes set to the value `0xff` the command
`BITPOS key 0` will return 24, since up to bit 23 all the bits are 1.

Basically, the function considers the right of the string as padded with zeros
if you look for clear bits and specify no range or the _start_ argument
**only**.

However, this behavior changes if you are looking for clear bits and specify a
range with both **start** and **end**. If no clear bit is found in the specified
range, the function returns -1 as the user specified a clear range and there are
no 0 bits in that range.

@examples

```cli
SET mykey "\xff\xf0\x00"
BITPOS mykey 0
SET mykey "\x00\xff\xf0"
BITPOS mykey 1 0
BITPOS mykey 1 2
set mykey "\x00\x00\x00"
BITPOS mykey 1
```
