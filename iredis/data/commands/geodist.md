Return the distance between two members in the geospatial index represented by
the sorted set.

Given a sorted set representing a geospatial index, populated using the `GEOADD`
command, the command returns the distance between the two specified members in
the specified unit.

If one or both the members are missing, the command returns NULL.

The unit must be one of the following, and defaults to meters:

- **m** for meters.
- **km** for kilometers.
- **mi** for miles.
- **ft** for feet.

The distance is computed assuming that the Earth is a perfect sphere, so errors
up to 0.5% are possible in edge cases.

@return

@bulk-string-reply, specifically:

The command returns the distance as a double (represented as a string) in the
specified unit, or NULL if one or both the elements are missing.

@examples

```cli
GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"
GEODIST Sicily Palermo Catania
GEODIST Sicily Palermo Catania km
GEODIST Sicily Palermo Catania mi
GEODIST Sicily Foo Bar
```
