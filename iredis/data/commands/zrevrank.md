Returns the rank of `member` in the sorted set stored at `key`, with the scores
ordered from high to low.
The rank (or index) is 0-based, which means that the member with the highest
score has rank `0`.

The optional `WITHSCORE` argument supplements the command's reply with the score of the element returned.

Use `ZRANK` to get the rank of an element with the scores ordered from low to
high.

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
ZREVRANK myzset "one"
ZREVRANK myzset "four"
ZREVRANK myzset "three" WITHSCORE
ZREVRANK myzset "four" WITHSCORE
```
