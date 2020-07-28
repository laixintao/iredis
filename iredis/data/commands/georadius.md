Return the members of a sorted set populated with geospatial information using
`GEOADD`, which are within the borders of the area specified with the center
location and the maximum distance from the center (the radius).

This manual page also covers the `GEORADIUS_RO` and `GEORADIUSBYMEMBER_RO`
variants (see the section below for more information).

The common use case for this command is to retrieve geospatial items near a
specified point not farther than a given amount of meters (or other units). This
allows, for example, to suggest mobile users of an application nearby places.

The radius is specified in one of the following units:

- **m** for meters.
- **km** for kilometers.
- **mi** for miles.
- **ft** for feet.

The command optionally returns additional information using the following
options:

- `WITHDIST`: Also return the distance of the returned items from the specified
  center. The distance is returned in the same unit as the unit specified as the
  radius argument of the command.
- `WITHCOORD`: Also return the longitude,latitude coordinates of the matching
  items.
- `WITHHASH`: Also return the raw geohash-encoded sorted set score of the item,
  in the form of a 52 bit unsigned integer. This is only useful for low level
  hacks or debugging and is otherwise of little interest for the general user.

The command default is to return unsorted items. Two different sorting methods
can be invoked using the following two options:

- `ASC`: Sort returned items from the nearest to the farthest, relative to the
  center.
- `DESC`: Sort returned items from the farthest to the nearest, relative to the
  center.

By default all the matching items are returned. It is possible to limit the
results to the first N matching items by using the **COUNT `<count>`** option.
However note that internally the command needs to perform an effort proportional
to the number of items matching the specified area, so to query very large areas
with a very small `COUNT` option may be slow even if just a few results are
returned. On the other hand `COUNT` can be a very effective way to reduce
bandwidth usage if normally just the first results are used.

By default the command returns the items to the client. It is possible to store
the results with one of these options:

- `!STORE`: Store the items in a sorted set populated with their geospatial
  information.
- `!STOREDIST`: Store the items in a sorted set populated with their distance
  from the center as a floating point number, in the same unit specified in the
  radius.

@return

@array-reply, specifically:

- Without any `WITH` option specified, the command just returns a linear array
  like ["New York","Milan","Paris"].
- If `WITHCOORD`, `WITHDIST` or `WITHHASH` options are specified, the command
  returns an array of arrays, where each sub-array represents a single item.

When additional information is returned as an array of arrays for each item, the
first item in the sub-array is always the name of the returned item. The other
information is returned in the following order as successive elements of the
sub-array.

1. The distance from the center as a floating point number, in the same unit
   specified in the radius.
2. The geohash integer.
3. The coordinates as a two items x,y array (longitude,latitude).

So for example the command `GEORADIUS Sicily 15 37 200 km WITHCOORD WITHDIST`
will return each item in the following way:

    ["Palermo","190.4424",["13.361389338970184","38.115556395496299"]]

## Read only variants

Since `GEORADIUS` and `GEORADIUSBYMEMBER` have a `STORE` and `STOREDIST` option
they are technically flagged as writing commands in the Redis command table. For
this reason read-only replicas will flag them, and Redis Cluster replicas will
redirect them to the master instance even if the connection is in read only mode
(See the `READONLY` command of Redis Cluster).

Breaking the compatibility with the past was considered but rejected, at least
for Redis 4.0, so instead two read only variants of the commands were added.
They are exactly like the original commands but refuse the `STORE` and
`STOREDIST` options. The two variants are called `GEORADIUS_RO` and
`GEORADIUSBYMEMBER_RO`, and can safely be used in replicas.

Both commands were introduced in Redis 3.2.10 and Redis 4.0.0 respectively.

@examples

```cli
GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"
GEORADIUS Sicily 15 37 200 km WITHDIST
GEORADIUS Sicily 15 37 200 km WITHCOORD
GEORADIUS Sicily 15 37 200 km WITHDIST WITHCOORD
```
