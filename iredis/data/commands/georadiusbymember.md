This command is exactly like `GEORADIUS` with the sole difference that instead
of taking, as the center of the area to query, a longitude and latitude value,
it takes the name of a member already existing inside the geospatial index
represented by the sorted set.

The position of the specified member is used as the center of the query.

Please check the example below and the `GEORADIUS` documentation for more
information about the command and its options.

Note that `GEORADIUSBYMEMBER_RO` is also available since Redis 3.2.10 and Redis
4.0.0 in order to provide a read-only command that can be used in replicas. See
the `GEORADIUS` page for more information.

@examples

```cli
GEOADD Sicily 13.583333 37.316667 "Agrigento"
GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"
GEORADIUSBYMEMBER Sicily Agrigento 100 km
```
