def test_wrong_stream_type(clean_redis, cli):
    clean_redis.lpush("mylist", "foo")
    cli.sendline("xrange mylist 0 -1")
    cli.expect("error")
    cli.expect("Invalid stream ID specified as stream command argument")


def test_wrong_stream_type_in_raw_mode(clean_redis, raw_cli):
    clean_redis.lpush("mylist", "foo")
    raw_cli.sendline("xrange mylist 0 -1")
    raw_cli.expect("ERROR")
    raw_cli.expect("Invalid stream ID specified as stream command argument")
