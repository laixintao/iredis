The command returns information about the current client connection's use of the [server assisted client side caching](/topics/client-side-caching) feature.

@return

@array-reply: a list of tracking information sections and their respective values, specifically:

* **flags**: A list of tracking flags used by the connection. The flags and their meanings are as follows:
  * `off`: The connection isn't using server assisted client side caching.
  * `on`: Server assisted client side caching is enabled for the connection.
  * `bcast`: The client uses broadcasting mode.
  * `optin`: The client does not cache keys by default.
  * `optout`: The client caches keys by default.
  * `caching-yes`: The next command will cache keys (exists only together with `optin`).
  * `caching-no`: The next command won't cache keys (exists only together with `optout`).
  * `noloop`: The client isn't notified about keys modified by itself.
  * `broken_redirect`: The client ID used for redirection isn't valid anymore.
* **redirect**: The client ID used for notifications redirection, or -1 when none.
* **prefixes**: A list of key prefixes for which notifications are sent to the client.
