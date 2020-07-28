The command treats a Redis string as a array of bits, and is capable of
addressing specific integer fields of varying bit widths and arbitrary non
(necessary) aligned offset. In practical terms using this command you can set,
for example, a signed 5 bits integer at bit offset 1234 to a specific value,
retrieve a 31 bit unsigned integer from offset 4567. Similarly the command
handles increments and decrements of the specified integers, providing
guaranteed and well specified overflow and underflow behavior that the user can
configure.

`BITFIELD` is able to operate with multiple bit fields in the same command call.
It takes a list of operations to perform, and returns an array of replies, where
each array matches the corresponding operation in the list of arguments.

For example the following command increments an 5 bit signed integer at bit
offset 100, and gets the value of the 4 bit unsigned integer at bit offset 0:

    > BITFIELD mykey INCRBY i5 100 1 GET u4 0
    1) (integer) 1
    2) (integer) 0

Note that:

1. Addressing with `GET` bits outside the current string length (including the
   case the key does not exist at all), results in the operation to be performed
   like the missing part all consists of bits set to 0.
2. Addressing with `SET` or `INCRBY` bits outside the current string length will
   enlarge the string, zero-padding it, as needed, for the minimal length
   needed, according to the most far bit touched.

## Supported subcommands and integer types

The following is the list of supported commands.

- **GET** `<type>` `<offset>` -- Returns the specified bit field.
- **SET** `<type>` `<offset>` `<value>` -- Set the specified bit field and
  returns its old value.
- **INCRBY** `<type>` `<offset>` `<increment>` -- Increments or decrements (if a
  negative increment is given) the specified bit field and returns the new
  value.

There is another subcommand that only changes the behavior of successive
`INCRBY` subcommand calls by setting the overflow behavior:

- **OVERFLOW** `[WRAP|SAT|FAIL]`

Where an integer type is expected, it can be composed by prefixing with `i` for
signed integers and `u` for unsigned integers with the number of bits of our
integer type. So for example `u8` is an unsigned integer of 8 bits and `i16` is
a signed integer of 16 bits.

The supported types are up to 64 bits for signed integers, and up to 63 bits for
unsigned integers. This limitation with unsigned integers is due to the fact
that currently the Redis protocol is unable to return 64 bit unsigned integers
as replies.

## Bits and positional offsets

There are two ways in order to specify offsets in the bitfield command. If a
number without any prefix is specified, it is used just as a zero based bit
offset inside the string.

However if the offset is prefixed with a `#` character, the specified offset is
multiplied by the integer type width, so for example:

    BITFIELD mystring SET i8 #0 100 SET i8 #1 200

Will set the first i8 integer at offset 0 and the second at offset 8. This way
you don't have to do the math yourself inside your client if what you want is a
plain array of integers of a given size.

## Overflow control

Using the `OVERFLOW` command the user is able to fine-tune the behavior of the
increment or decrement overflow (or underflow) by specifying one of the
following behaviors:

- **WRAP**: wrap around, both with signed and unsigned integers. In the case of
  unsigned integers, wrapping is like performing the operation modulo the
  maximum value the integer can contain (the C standard behavior). With signed
  integers instead wrapping means that overflows restart towards the most
  negative value and underflows towards the most positive ones, so for example
  if an `i8` integer is set to the value 127, incrementing it by 1 will yield
  `-128`.
- **SAT**: uses saturation arithmetic, that is, on underflows the value is set
  to the minimum integer value, and on overflows to the maximum integer value.
  For example incrementing an `i8` integer starting from value 120 with an
  increment of 10, will result into the value 127, and further increments will
  always keep the value at 127. The same happens on underflows, but towards the
  value is blocked at the most negative value.
- **FAIL**: in this mode no operation is performed on overflows or underflows
  detected. The corresponding return value is set to NULL to signal the
  condition to the caller.

Note that each `OVERFLOW` statement only affects the `INCRBY` commands that
follow it in the list of subcommands, up to the next `OVERFLOW` statement.

By default, **WRAP** is used if not otherwise specified.

    > BITFIELD mykey incrby u2 100 1 OVERFLOW SAT incrby u2 102 1
    1) (integer) 1
    2) (integer) 1
    > BITFIELD mykey incrby u2 100 1 OVERFLOW SAT incrby u2 102 1
    1) (integer) 2
    2) (integer) 2
    > BITFIELD mykey incrby u2 100 1 OVERFLOW SAT incrby u2 102 1
    1) (integer) 3
    2) (integer) 3
    > BITFIELD mykey incrby u2 100 1 OVERFLOW SAT incrby u2 102 1
    1) (integer) 0
    2) (integer) 3

## Return value

The command returns an array with each entry being the corresponding result of
the sub command given at the same position. `OVERFLOW` subcommands don't count
as generating a reply.

The following is an example of `OVERFLOW FAIL` returning NULL.

    > BITFIELD mykey OVERFLOW FAIL incrby u2 102 1
    1) (nil)

## Motivations

The motivation for this command is that the ability to store many small integers
as a single large bitmap (or segmented over a few keys to avoid having huge
keys) is extremely memory efficient, and opens new use cases for Redis to be
applied, especially in the field of real time analytics. This use cases are
supported by the ability to specify the overflow in a controlled way.

Fun fact: Reddit's 2017 April fools' project
[r/place](https://reddit.com/r/place) was
[built using the Redis BITFIELD command](https://redditblog.com/2017/04/13/how-we-built-rplace/)
in order to take an in-memory representation of the collaborative canvas.

## Performance considerations

Usually `BITFIELD` is a fast command, however note that addressing far bits of
currently short strings will trigger an allocation that may be more costly than
executing the command on bits already existing.

## Orders of bits

The representation used by `BITFIELD` considers the bitmap as having the bit
number 0 to be the most significant bit of the first byte, and so forth, so for
example setting a 5 bits unsigned integer to value 23 at offset 7 into a bitmap
previously set to all zeroes, will produce the following representation:

    +--------+--------+
    |00000001|01110000|
    +--------+--------+

When offsets and integer sizes are aligned to bytes boundaries, this is the same
as big endian, however when such alignment does not exist, its important to also
understand how the bits inside a byte are ordered.
