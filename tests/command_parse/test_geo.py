def test_geoadd(judge_command):
    judge_command(
        'GEOADD Sicily 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"',
        {
            "command": "GEOADD",
            "key": "Sicily",
            "longitude": "15.087269",
            "latitude": "37.502669",
            "member": '"Catania"',
        },
    )


def test_georadiusbymember(judge_command):
    judge_command(
        "GEORADIUSBYMEMBER Sicily Agrigento 100 km",
        {
            "command": "GEORADIUSBYMEMBER",
            "key": "Sicily",
            "member": "Agrigento",
            "float": "100",
            "distunit": "km",
        },
    )


def test_georadius(judge_command):
    judge_command(
        "GEORADIUS Sicily 15 37 200 km WITHDIST WITHCOORD ",
        {
            "command": "GEORADIUS",
            "key": "Sicily",
            "longitude": "15",
            "latitude": "37",
            "float": "200",
            "distunit": "km",
            "geochoice": "WITHCOORD",
        },
    )
