The command returns the index of matching elements inside a Redis list. By
default, when no options are given, it will scan the list from head to tail,
looking for the first match of "element". If the element is found, its index
(the zero-based position in the list) is returned. Otherwise, if no match is
found, NULL is returned.

```
> RPUSH mylist a b c 1 2 3 c c
> LPOS mylist c
2
```

The optional arguments and options can modify the command's behavior. The `RANK`
option specifies the "rank" of the first element to return, in case there are
multiple matches. A rank of 1 means to return the first match, 2 to return the
second match, and so forth.

For instance, in the above example the element "c" is present multiple times, if
I want the index of the second match, I'll write:

```
> LPOS mylist c RANK 2
6
```

That is, the second occurrence of "c" is at position 6. A negative "rank" as the
`RANK` argument tells `LPOS` to invert the search direction, starting from the
tail to the head.

So, we want to say, give me the first element starting from the tail of the
list:

```
> LPOS mylist c RANK -1
7
```

Note that the indexes are still reported in the "natural" way, that is,
considering the first element starting from the head of the list at index 0, the
next element at index 1, and so forth. This basically means that the returned
indexes are stable whatever the rank is positive or negative.

Sometimes we want to return not just the Nth matching element, but the position
of all the first N matching elements. This can be achieved using the `COUNT`
option.

```
> LPOS mylist c COUNT 2
[2,6]
```

We can combine `COUNT` and `RANK`, so that `COUNT` will try to return up to the
specified number of matches, but starting from the Nth match, as specified by
the `RANK` option.

```
> LPOS mylist c RANK -1 COUNT 2
[7,6]
```

When `COUNT` is used, it is possible to specify 0 as the number of matches, as a
way to tell the command we want all the matches found returned as an array of
indexes. This is better than giving a very large `COUNT` option because it is
more general.

```
> LPOS mylist COUNT 0
[2,6,7]
```

When `COUNT` is used and no match is found, an empty array is returned. However
when `COUNT` is not used and there are no matches, the command returns NULL.

Finally, the `MAXLEN` option tells the command to compare the provided element
only with a given maximum number of list items. So for instance specifying
`MAXLEN 1000` will make sure that the command performs only 1000 comparisons,
effectively running the algorithm on a subset of the list (the first part or the
last part depending on the fact we use a positive or negative rank). This is
useful to limit the maximum complexity of the command. It is also useful when we
expect the match to be found very early, but want to be sure that in case this
is not true, the command does not take too much time to run.

@return

The command returns the integer representing the matching element, or null if
there is no match. However, if the `COUNT` option is given the command returns
an array (empty if there are no matches).

@examples

```cli
RPUSH mylist a b c d 1 2 3 4 3 3 3
LPOS mylist 3
LPOS mylist 3 COUNT 0 RANK 2
```
