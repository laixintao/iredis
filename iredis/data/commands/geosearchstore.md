This command is like `GEOSEARCH`, but stores the result in destination key.

This command comes in place of the now deprecated `GEORADIUS` and
`GEORADIUSBYMEMBER`.

By default, it stores the results in the `destination` sorted set with their
geospatial information.

When using the `STOREDIST` option, the command stores the items in a sorted set
populated with their distance from the center of the circle or box, as a
floating-point number, in the same unit specified for that shape.
