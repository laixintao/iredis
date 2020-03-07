Geospatial Redis commands encode positions of objects in a single 52 bit
integer, using a technique called geohash. Those 52 bit integers are:

1. Returned by `GEOAENCODE` as return value.
2. Used by `GEOADD` as sorted set scores of members.

The `GEODECODE` command is able to translate the 52 bit integers back into a
position expressed as longitude and latitude. The command also returns the
corners of the box that the 52 bit integer identifies on the earth surface,
since each 52 integer actually represent not a single point, but a small area.

This command usefulness is limited to the rare situations where you want to
fetch raw data from the sorted set, for example with `ZRANGE`, and later need to
decode the scores into positions. The other obvious use is debugging.

@return

@array-reply, specifically:

The command returns an array of three elements. Each element of the main array
is an array of two elements, specifying a longitude and a latitude. So the
returned value is in the following form:

- center-longitude, center-latitude
- min-longitude, min-latitude
- max-longitude, max-latitude

@examples

```cli
GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"
ZSCORE Sicily "Palermo"
GEODECODE 3479099956230698
```
