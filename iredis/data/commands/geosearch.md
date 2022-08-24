Return the members of a sorted set populated with geospatial information using `GEOADD`, which are within the borders of the area specified by a given shape. This command extends the `GEORADIUS` command, so in addition to searching within circular areas, it supports searching within rectangular areas.

This command should be used in place of the deprecated `GEORADIUS` and `GEORADIUSBYMEMBER` commands.

The query's center point is provided by one of these mandatory options:

* `FROMMEMBER`: Use the position of the given existing `<member>` in the sorted set.
* `FROMLONLAT`: Use the given `<longitude>` and `<latitude>` position.

The query's shape is provided by one of these mandatory options:

* `BYRADIUS`: Similar to `GEORADIUS`, search inside circular area according to given `<radius>`.
* `BYBOX`: Search inside an axis-aligned rectangle, determined by `<height>` and `<width>`.

The command optionally returns additional information using the following options:

* `WITHDIST`: Also return the distance of the returned items from the specified center point. The distance is returned in the same unit as specified for the radius or height and width arguments.
* `WITHCOORD`: Also return the longitude and latitude of the matching items.
* `WITHHASH`: Also return the raw geohash-encoded sorted set score of the item, in the form of a 52 bit unsigned integer. This is only useful for low level hacks or debugging and is otherwise of little interest for the general user.

Matching items are returned unsorted by default. To sort them, use one of the following two options:

* `ASC`: Sort returned items from the nearest to the farthest, relative to the center point.
* `DESC`: Sort returned items from the farthest to the nearest, relative to the center point.

All matching items are returned by default. To limit the results to the first N matching items, use the **COUNT `<count>`** option.
When the `ANY` option is used, the command returns as soon as enough matches are found.  This means that the results returned may not be the ones closest to the specified point, but the effort invested by the server to generate them is significantly less.
When `ANY` is not provided, the command will perform an effort that is proportional to the number of items matching the specified area and sort them,
so to query very large areas with a very small `COUNT` option may be slow even if just a few results are returned.

@return

@array-reply, specifically:

* Without any `WITH` option specified, the command just returns a linear array like ["New York","Milan","Paris"].
* If `WITHCOORD`, `WITHDIST` or `WITHHASH` options are specified, the command returns an array of arrays, where each sub-array represents a single item.

When additional information is returned as an array of arrays for each item, the first item in the sub-array is always the name of the returned item. The other information is returned in the following order as successive elements of the sub-array.

1. The distance from the center as a floating point number, in the same unit specified in the shape.
2. The geohash integer.
3. The coordinates as a two items x,y array (longitude,latitude).

@examples

```cli
GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"
GEOADD Sicily 12.758489 38.788135 "edge1"   17.241510 38.788135 "edge2" 
GEOSEARCH Sicily FROMLONLAT 15 37 BYRADIUS 200 km ASC
GEOSEARCH Sicily FROMLONLAT 15 37 BYBOX 400 400 km ASC WITHCOORD WITHDIST
```
