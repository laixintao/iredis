Sets or clears the bit at _offset_ in the string value stored at _key_.

The bit is either set or cleared depending on _value_, which can be either 0
or 1.

When _key_ does not exist, a new string value is created. The string is grown to
make sure it can hold a bit at _offset_. The _offset_ argument is required to be
greater than or equal to 0, and smaller than 2^32 (this limits bitmaps to
512MB). When the string at _key_ is grown, added bits are set to 0.

**Warning**: When setting the last possible bit (_offset_ equal to 2^32 -1) and
the string value stored at _key_ does not yet hold a string value, or holds a
small string value, Redis needs to allocate all intermediate memory which can
block the server for some time. On a 2010 MacBook Pro, setting bit number 2^32
-1 (512MB allocation) takes ~300ms, setting bit number 2^30 -1 (128MB
allocation) takes ~80ms, setting bit number 2^28 -1 (32MB allocation) takes
~30ms and setting bit number 2^26 -1 (8MB allocation) takes ~8ms. Note that once
this first allocation is done, subsequent calls to `SETBIT` for the same _key_
will not have the allocation overhead.

@return

@integer-reply: the original bit value stored at _offset_.

@examples

```cli
SETBIT mykey 7 1
SETBIT mykey 7 0
GET mykey
```

## Pattern: accessing the entire bitmap

There are cases when you need to set all the bits of single bitmap at once, for
example when initializing it to a default non-zero value. It is possible to do
this with multiple calls to the `SETBIT` command, one for each bit that needs to
be set. However, so as an optimization you can use a single `SET` command to set
the entire bitmap.

Bitmaps are not an actual data type, but a set of bit-oriented operations
defined on the String type (for more information refer to the [Bitmaps section
of the Data Types Introduction page][ti]). This means that bitmaps can be used
with string commands, and most importantly with `SET` and `GET`.

Because Redis' strings are binary-safe, a bitmap is trivially encoded as a bytes
stream. The first byte of the string corresponds to offsets 0..7 of the bitmap,
the second byte to the 8..15 range, and so forth.

For example, after setting a few bits, getting the string value of the bitmap
would look like this:

```
> SETBIT bitmapsarestrings 2 1
> SETBIT bitmapsarestrings 3 1
> SETBIT bitmapsarestrings 5 1
> SETBIT bitmapsarestrings 10 1
> SETBIT bitmapsarestrings 11 1
> SETBIT bitmapsarestrings 14 1
> GET bitmapsarestrings
"42"
```

By getting the string representation of a bitmap, the client can then parse the
response's bytes by extracting the bit values using native bit operations in its
native programming language. Symmetrically, it is also possible to set an entire
bitmap by performing the bits-to-bytes encoding in the client and calling `SET`
with the resultant string.

[ti]: /topics/data-types-intro#bitmaps

## Pattern: setting multiple bits

`SETBIT` excels at setting single bits, and can be called several times when
multiple bits need to be set. To optimize this operation you can replace
multiple `SETBIT` calls with a single call to the variadic `BITFIELD` command
and the use of fields of type `u1`.

For example, the example above could be replaced by:

```
> BITFIELD bitsinabitmap SET u1 2 1 SET u1 3 1 SET u1 5 1 SET u1 10 1 SET u1 11 1 SET u1 14 1
```

## Advanced Pattern: accessing bitmap ranges

It is also possible to use the `GETRANGE` and `SETRANGE` string commands to
efficiently access a range of bit offsets in a bitmap. Below is a sample
implementation in idiomatic Redis Lua scripting that can be run with the `EVAL`
command:

```
--[[
Sets a bitmap range

Bitmaps are stored as Strings in Redis. A range spans one or more bytes,
so we can call `SETRANGE` when entire bytes need to be set instead of flipping
individual bits. Also, to avoid multiple internal memory allocations in
Redis, we traverse in reverse.
Expected input:
  KEYS[1] - bitfield key
  ARGV[1] - start offset (0-based, inclusive)
  ARGV[2] - end offset (same, should be bigger than start, no error checking)
  ARGV[3] - value (should be 0 or 1, no error checking)
]]--

-- A helper function to stringify a binary string to semi-binary format
local function tobits(str)
  local r = ''
  for i = 1, string.len(str) do
    local c = string.byte(str, i)
    local b = ' '
    for j = 0, 7 do
      b = tostring(bit.band(c, 1)) .. b
      c = bit.rshift(c, 1)
    end
    r = r .. b
  end
  return r
end

-- Main
local k = KEYS[1]
local s, e, v = tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3])

-- First treat the dangling bits in the last byte
local ms, me = s % 8, (e + 1) % 8
if me > 0 then
  local t = math.max(e - me + 1, s)
  for i = e, t, -1 do
    redis.call('SETBIT', k, i, v)
  end
  e = t
end

-- Then the danglings in the first byte
if ms > 0 then
  local t = math.min(s - ms + 7, e)
  for i = s, t, 1 do
    redis.call('SETBIT', k, i, v)
  end
  s = t + 1
end

-- Set a range accordingly, if at all
local rs, re = s / 8, (e + 1) / 8
local rl = re - rs
if rl > 0 then
  local b = '\255'
  if 0 == v then
    b = '\0'
  end
  redis.call('SETRANGE', k, rs, string.rep(b, rl))
end
```

**Note:** the implementation for getting a range of bit offsets from a bitmap is
left as an exercise to the reader.
