The STRALGO implements complex algorithms that operate on strings. Right now the
only algorithm implemented is the LCS algorithm (longest common substring).
However new algorithms could be implemented in the future. The goal of this
command is to provide to Redis users algorithms that need fast implementations
and are normally not provided in the standard library of most programming
languages.

The first argument of the command selects the algorithm to use, right now the
argument must be "LCS", since this is the only implemented one.

## LCS algorithm

```
STRALGO LCS [KEYS ...] [STRINGS ...] [LEN] [IDX] [MINMATCHLEN <len>] [WITHMATCHLEN]
```

The LCS subcommand implements the longest common subsequence algorithm. Note
that this is different than the longest common string algorithm, since matching
characters in the string does not need to be contiguous.

For instance the LCS between "foo" and "fao" is "fo", since scanning the two
strings from left to right, the longest common set of characters is composed of
the first "f" and then the "o".

LCS is very useful in order to evaluate how similar two strings are. Strings can
represent many things. For instance if two strings are DNA sequences, the LCS
will provide a measure of similarity between the two DNA sequences. If the
strings represent some text edited by some user, the LCS could represent how
different the new text is compared to the old one, and so forth.

Note that this algorithm runs in `O(N*M)` time, where N is the length of the
first string and M is the length of the second string. So either spin a
different Redis instance in order to run this algorithm, or make sure to run it
against very small strings.

The basic usage is the following:

```
> STRALGO LCS STRINGS ohmytext mynewtext
"mytext"
```

It is also possible to compute the LCS between the content of two keys:

```
> MSET key1 ohmytext key2 mynewtext
OK
> STRALGO LCS KEYS key1 key2
"mytext"
```

Sometimes we need just the length of the match:

```
> STRALGO LCS STRINGS ohmytext mynewtext LEN
6
```

However what is often very useful, is to know the match position in each
strings:

```
> STRALGO LCS KEYS key1 key2 IDX
1) "matches"
2) 1) 1) 1) (integer) 4
         2) (integer) 7
      2) 1) (integer) 5
         2) (integer) 8
   2) 1) 1) (integer) 2
         2) (integer) 3
      2) 1) (integer) 0
         2) (integer) 1
3) "len"
4) (integer) 6
```

Matches are produced from the last one to the first one, since this is how the
algorithm works, and it more efficient to emit things in the same order. The
above array means that the first match (second element of the array) is between
positions 2-3 of the first string and 0-1 of the second. Then there is another
match between 4-7 and 5-8.

To restrict the list of matches to the ones of a given minimal length:

```
> STRALGO LCS KEYS key1 key2 IDX MINMATCHLEN 4
1) "matches"
2) 1) 1) 1) (integer) 4
         2) (integer) 7
      2) 1) (integer) 5
         2) (integer) 8
3) "len"
4) (integer) 6
```

Finally to also have the match len:

```
> STRALGO LCS KEYS key1 key2 IDX MINMATCHLEN 4 WITHMATCHLEN
1) "matches"
2) 1) 1) 1) (integer) 4
         2) (integer) 7
      2) 1) (integer) 5
         2) (integer) 8
      3) (integer) 4
3) "len"
4) (integer) 6
```

@return

For the LCS algorithm:

- Without modifiers the string representing the longest common substring is
  returned.
- When LEN is given the command returns the length of the longest common
  substring.
- When IDX is given the command returns an array with the LCS length and all the
  ranges in both the strings, start and end offset for each string, where there
  are matches. When WITHMATCHLEN is given each array representing a match will
  also have the length of the match (see examples).
