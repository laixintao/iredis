from redis import connection

conn = connection.Connection()


# COMMAND EXECUTION AND PROTOCOL PARSING
def execute_command(*args, **options):
    "Execute a command and return a parsed response"
    command_name = args[0]
    try:
        conn.send_command(*args)
        return parse_response(conn, command_name, **options)
    except (ConnectionError, TimeoutError) as e:
        conn.disconnect()
        if not (conn.retry_on_timeout and isinstance(e, TimeoutError)):
            raise
        conn.send_command(*args)
        return parse_response(conn, command_name, **options)


def parse_response(connection, command_name, **options):
    "Parses a response from the Redis server"
    try:
        response = connection.read_response()
    except ResponseError:
        if EMPTY_RESPONSE in options:
            return options[EMPTY_RESPONSE]
        raise
    # TODO
    # resp callback
    return response


def send_command(command):
    return execute_command(command)


resp = send_command("keys *")
print(resp)
