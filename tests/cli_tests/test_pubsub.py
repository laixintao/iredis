def test_subscribe(cli, clean_redis):
    cli.sendline("subscribe foo")
    cli.expect("subscribe from")
    cli.expect("foo")
    cli.expect("1")

    clean_redis.publish("foo", "test message")
    cli.expect("from")
    cli.expect("foo")
    cli.expect("test message")

    # unsubscribe, send ctrl-c
    cli.send(chr(3))
    cli.expect("unsubscribe from")
    cli.expect("0")


def test_subscribe_in_raw_mode(raw_cli, clean_redis):
    raw_cli.sendline("subscribe foo")
    raw_cli.expect("subscribe\r")
    raw_cli.expect("foo\r")
    raw_cli.expect("1\r")

    clean_redis.publish("foo", "test message")
    raw_cli.expect("message\r")
    raw_cli.expect("foo\r")
    raw_cli.expect("test message")

    # unsubscribe, send ctrl-c
    raw_cli.send(chr(3))
    raw_cli.expect("0\r")
