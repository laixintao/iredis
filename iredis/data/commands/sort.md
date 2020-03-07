Returns or stores the elements contained in the [list][tdtl], [set][tdts] or
[sorted set][tdtss] at `key`. By default, sorting is numeric and elements are
compared by their value interpreted as double precision floating point number.
This is `SORT` in its simplest form:

[tdtl]: /topics/data-types#lists
[tdts]: /topics/data-types#set
[tdtss]: /topics/data-types#sorted-sets

```
SORT mylist
```

Assuming `mylist` is a list of numbers, this command will return the same list
with the elements sorted from small to large. In order to sort the numbers from
large to small, use the `!DESC` modifier:

```
SORT mylist DESC
```

When `mylist` contains string values and you want to sort them
lexicographically, use the `!ALPHA` modifier:

```
SORT mylist ALPHA
```

Redis is UTF-8 aware, assuming you correctly set the `!LC_COLLATE` environment
variable.

The number of returned elements can be limited using the `!LIMIT` modifier. This
modifier takes the `offset` argument, specifying the number of elements to skip
and the `count` argument, specifying the number of elements to return from
starting at `offset`. The following example will return 10 elements of the
sorted version of `mylist`, starting at element 0 (`offset` is zero-based):

```
SORT mylist LIMIT 0 10
```

Almost all modifiers can be used together. The following example will return the
first 5 elements, lexicographically sorted in descending order:

```
SORT mylist LIMIT 0 5 ALPHA DESC
```

## Sorting by external keys

Sometimes you want to sort elements using external keys as weights to compare
instead of comparing the actual elements in the list, set or sorted set. Let's
say the list `mylist` contains the elements `1`, `2` and `3` representing unique
IDs of objects stored in `object_1`, `object_2` and `object_3`. When these
objects have associated weights stored in `weight_1`, `weight_2` and `weight_3`,
`SORT` can be instructed to use these weights to sort `mylist` with the
following statement:

```
SORT mylist BY weight_*
```

The `BY` option takes a pattern (equal to `weight_*` in this example) that is
used to generate the keys that are used for sorting. These key names are
obtained substituting the first occurrence of `*` with the actual value of the
element in the list (`1`, `2` and `3` in this example).

## Skip sorting the elements

The `!BY` option can also take a non-existent key, which causes `SORT` to skip
the sorting operation. This is useful if you want to retrieve external keys (see
the `!GET` option below) without the overhead of sorting.

```
SORT mylist BY nosort
```

## Retrieving external keys

Our previous example returns just the sorted IDs. In some cases, it is more
useful to get the actual objects instead of their IDs (`object_1`, `object_2`
and `object_3`). Retrieving external keys based on the elements in a list, set
or sorted set can be done with the following command:

```
SORT mylist BY weight_* GET object_*
```

The `!GET` option can be used multiple times in order to get more keys for every
element of the original list, set or sorted set.

It is also possible to `!GET` the element itself using the special pattern `#`:

```
SORT mylist BY weight_* GET object_* GET #
```

## Storing the result of a SORT operation

By default, `SORT` returns the sorted elements to the client. With the `!STORE`
option, the result will be stored as a list at the specified key instead of
being returned to the client.

```
SORT mylist BY weight_* STORE resultkey
```

An interesting pattern using `SORT ... STORE` consists in associating an
`EXPIRE` timeout to the resulting key so that in applications where the result
of a `SORT` operation can be cached for some time. Other clients will use the
cached list instead of calling `SORT` for every request. When the key will
timeout, an updated version of the cache can be created by calling
`SORT ... STORE` again.

Note that for correctly implementing this pattern it is important to avoid
multiple clients rebuilding the cache at the same time. Some kind of locking is
needed here (for instance using `SETNX`).

## Using hashes in `!BY` and `!GET`

It is possible to use `!BY` and `!GET` options against hash fields with the
following syntax:

```
SORT mylist BY weight_*->fieldname GET object_*->fieldname
```

The string `->` is used to separate the key name from the hash field name. The
key is substituted as documented above, and the hash stored at the resulting key
is accessed to retrieve the specified hash field.

@return

@array-reply: without passing the `store` option the command returns a list of
sorted elements. @integer-reply: when the `store` option is specified the
command returns the number of sorted elements in the destination list.
