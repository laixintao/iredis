Geospatial Redis commands encode positions of objects in a single 52 bit
integer, using a technique called geohash. The encoding is further explained in
the `GEODECODE` and `GEOADD` documentation. The `GEOENCODE` command, documented
in this page, is able to convert a longitude and latitude pair into such 52 bit
integer, which is used as the _score_ for the sorted set members representing
geopositional information.

Normally you don't need to use this command, unless you plan to implement low
level code in the client side interacting with the Redis geo commands. This
command may also be useful for debugging purposes.

`GEOENCODE` takes as input:

1. The longitude and latitude of a point on the Earth surface.
2. Optionally a radius represented by an integer and an unit.

And returns a set of information, including the representation of the position
as a 52 bit integer, the min and max corners of the bounding box represented by
the geo hash, the center point in the area covered by the geohash integer, and
finally the two sorted set scores to query in order to retrieve all the elements
included in the geohash area.

The radius optionally provided to the command is used in order to compute the
two scores returned by the command for range query purposes. Moreover the
returned geohash integer will only have the most significant bits set, according
to the number of bits needed to approximate the specified radius.

## Use case

As already specified this command is mostly not needed if not for debugging.
However there are actual use cases, which is, when there is to query for the
same areas multiple times, or with a different granularity or area shape
compared to what Redis `GEORADIUS` is able to provide, the client may implement
using this command part of the logic on the client side. Score ranges
representing given areas can be cached client side and used to retrieve elements
directly using `ZRANGEBYSCORE`.

@return

@array-reply, specifically:

The command returns an array of give elements in the following order:

- The 52 bit geohash
- min-longitude, min-latitude of the area identified
- max-longitude, max-latitude of the area identified
- center-longitude, center-latitude
- min-score and max-score of the sorted set to retrieve the members inside the
  area

@examples

```cli
GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"
ZSCORE Sicily "Palermo"
GEOENCODE 13.361389 38.115556 100 km
```
