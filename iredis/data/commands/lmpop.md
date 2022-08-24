Pops one or more elements from the first non-empty list key from the list of provided key names.

`LMPOP` and `BLMPOP` are similar to the following, more limited, commands:

- `LPOP` or `RPOP` which take only one key, and can return multiple elements.
- `BLPOP` or `BRPOP` which take multiple keys, but return only one element from just one key.

See `BLMPOP` for the blocking variant of this command.

Elements are popped from either the left or right of the first non-empty list based on the passed argument.
The number of returned elements is limited to the lower between the non-empty list's length, and the count argument (which defaults to 1).

@return

@array-reply: specifically:

* A `nil` when no element could be popped.
* A two-element array with the first element being the name of the key from which elements were popped, and the second element is an array of elements.

@examples

```cli
LMPOP 2 non1 non2 LEFT COUNT 10
LPUSH mylist "one" "two" "three" "four" "five"
LMPOP 1 mylist LEFT
LRANGE mylist 0 -1
LMPOP 1 mylist RIGHT COUNT 10
LPUSH mylist "one" "two" "three" "four" "five"
LPUSH mylist2 "a" "b" "c" "d" "e"
LMPOP 2 mylist mylist2 right count 3
LRANGE mylist 0 -1
LMPOP 2 mylist mylist2 right count 5
LMPOP 2 mylist mylist2 right count 10
EXISTS mylist mylist2
```
