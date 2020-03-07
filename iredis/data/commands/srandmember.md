When called with just the `key` argument, return a random element from the set
value stored at `key`.

Starting from Redis version 2.6, when called with the additional `count`
argument, return an array of `count` **distinct elements** if `count` is
positive. If called with a negative `count` the behavior changes and the command
is allowed to return the **same element multiple times**. In this case the
number of returned elements is the absolute value of the specified `count`.

When called with just the key argument, the operation is similar to `SPOP`,
however while `SPOP` also removes the randomly selected element from the set,
`SRANDMEMBER` will just return a random element without altering the original
set in any way.

@return

@bulk-string-reply: without the additional `count` argument the command returns
a Bulk Reply with the randomly selected element, or `nil` when `key` does not
exist. @array-reply: when the additional `count` argument is passed the command
returns an array of elements, or an empty array when `key` does not exist.

@examples

```cli
SADD myset one two three
SRANDMEMBER myset
SRANDMEMBER myset 2
SRANDMEMBER myset -5
```

## Specification of the behavior when count is passed

When a count argument is passed and is positive, the elements are returned as if
every selected element is removed from the set (like the extraction of numbers
in the game of Bingo). However elements are **not removed** from the Set. So
basically:

- No repeated elements are returned.
- If count is bigger than the number of elements inside the Set, the command
  will only return the whole set without additional elements.

When instead the count is negative, the behavior changes and the extraction
happens as if you put the extracted element inside the bag again after every
extraction, so repeated elements are possible, and the number of elements
requested is always returned as we can repeat the same elements again and again,
with the exception of an empty Set (non existing key) that will always produce
an empty array as a result.

## Distribution of returned elements

The distribution of the returned elements is far from perfect when the number of
elements in the set is small, this is due to the fact that we used an
approximated random element function that does not really guarantees good
distribution.

The algorithm used, that is implemented inside dict.c, samples the hash table
buckets to find a non-empty one. Once a non empty bucket is found, since we use
chaining in our hash table implementation, the number of elements inside the
bucket is checked and a random element is selected.

This means that if you have two non-empty buckets in the entire hash table, and
one has three elements while one has just one, the element that is alone in its
bucket will be returned with much higher probability.
