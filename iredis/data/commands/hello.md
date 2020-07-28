Switch the connection to a different protocol. Redis version 6 or greater are
able to support two protocols, the old protocol, RESP2, and a new one introduced
with Redis 6, RESP3. RESP3 has certain advantages since when the connection is
in this mode, Redis is able to reply with more semantical replies: for instance
`HGETALL` will return a _map type_, so a client library implementation no longer
requires to know in advance to translate the array into a hash before returning
it to the caller. For a full coverage of RESP3 please
[check this repository](https://github.com/antirez/resp3).

Redis 6 connections starts in RESP2 mode, so clients implementing RESP2 do not
need to change (nor there are short term plans to drop support for RESP2).
Clients that want to handshake the RESP3 mode need to call the `HELLO` command,
using "3" as first argument.

    > HELLO 3
    1# "server" => "redis"
    2# "version" => "6.0.0"
    3# "proto" => (integer) 3
    4# "id" => (integer) 10
    5# "mode" => "standalone"
    6# "role" => "master"
    7# "modules" => (empty array)

The `HELLO` command has a useful reply that will state a number of facts about
the server: the exact version, the set of modules loaded, the client ID, the
replication role and so forth. Because of that, and given that the `HELLO`
command also works with "2" as argument, both in order to downgrade the protocol
back to version 2, or just to get the reply from the server without switching
the protocol, client library authors may consider using this command instead of
the canonical `PING` when setting up the connection.

This command accepts two non mandatory options:

- `AUTH <username> <password>`: directly authenticate the connection other than
  switching to the specified protocol. In this way there is no need to call
  `AUTH` before `HELLO` when setting up new connections. Note that the username
  can be set to "default" in order to authenticate against a server that does
  not use ACLs, but the simpler `requirepass` mechanism of Redis before
  version 6.
- `SETNAME <clientname>`: this is equivalent to also call `CLIENT SETNAME`.

@return

@array-reply: a list of server properties. The reply is a map instead of an
array when RESP3 is selected. The command returns an error if the protocol
requested does not exist.
