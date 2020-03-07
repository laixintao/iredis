Return the UNIX TIME of the last DB save executed with success. A client may
check if a `BGSAVE` command succeeded reading the `LASTSAVE` value, then issuing
a `BGSAVE` command and checking at regular intervals every N seconds if
`LASTSAVE` changed.

@return

@integer-reply: an UNIX time stamp.
