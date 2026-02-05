Returns the rank of `member` in the sorted set stored at `key`, with the scores
ordered from low to high.
The rank (or index) is 0-based, which means that the member with the lowest
score has rank `0`.

The optional `WITHSCORE` argument supplements the command's reply with the score of the element returned.

Use `ZREVRANK` to get the rank of an element with the scores ordered from high
to low.

@return

* If `member` exists in the sorted set:
  * using `WITHSCORE`, @array-reply: an array containing the rank and score of `member`.
  * without using `WITHSCORE`, @integer-reply: the rank of `member`.
* If `member` does not exist in the sorted set or `key` does not exist:
  * using `WITHSCORE`, @array-reply: `nil`.
  * without using `WITHSCORE`, @bulk-string-reply: `nil`.
  
Note that in RESP3 null and nullarray are the same, but in RESP2 they are not.

@examples

```cli
ZADD myzset 1 "one"
ZADD myzset 2 "two"
ZADD myzset 3 "three"
ZRANK myzset "three"
ZRANK myzset "four"
ZRANK myzset "three" WITHSCORE
ZRANK myzset "four" WITHSCORE
```
