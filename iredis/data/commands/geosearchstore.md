This command is like `GEOSEARCH`, but stores the result in destination key.

This command comes in place of the now deprecated `GEORADIUS` and `GEORADIUSBYMEMBER`.

By default, it stores the results in the `destination` sorted set with their geospatial information.

When using the `STOREDIST` option, the command stores the items in a sorted set populated with their distance from the center of the circle or box, as a floating-point number, in the same unit specified for that shape.

@return

@integer-reply: the number of elements in the resulting set.

@examples

```cli
GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"
GEOADD Sicily 12.758489 38.788135 "edge1"   17.241510 38.788135 "edge2" 
GEOSEARCHSTORE key1 Sicily FROMLONLAT 15 37 BYBOX 400 400 km ASC COUNT 3
GEOSEARCH key1 FROMLONLAT 15 37 BYBOX 400 400 km ASC WITHCOORD WITHDIST WITHHASH
GEOSEARCHSTORE key2 Sicily FROMLONLAT 15 37 BYBOX 400 400 km ASC COUNT 3 STOREDIST
ZRANGE key2 0 -1 WITHSCORES
```