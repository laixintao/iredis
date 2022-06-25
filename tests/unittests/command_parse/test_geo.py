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
    judge_command(
        'GEOADD Sicily NX CH 13.361389 38.115556 "Palermo" 15.087269 37.502669 "Catania"',
        {
            "command": "GEOADD",
            "condition": "NX",
            "changed": "CH",
            "key": "Sicily",
            "longitude": "15.087269",
            "latitude": "37.502669",
            "member": '"Catania"',
        },
    )


def test_geosearch(judge_command):
    judge_command(
        "GEOSEARCH Sicily FROMLONLAT 15 37 BYBOX 400 400 km ASC WITHCOORD WITHDIST",
        {
            "command": "GEOSEARCH",
            "key": "Sicily",
            "any": "FROMLONLAT 15 37 BYBOX 400 400 km ASC WITHCOORD WITHDIST",
        },
    )


def test_geosearchstore(judge_command):
    judge_command(
        "GEOSEARCHSTORE key2 Sicily FROMLONLAT 15 37 BYBOX 400 400 km ASC COUNT 3 STOREDIST",
        {
            "command": "GEOSEARCHSTORE",
            "key": ["Sicily", "key2"],
            "any": "FROMLONLAT 15 37 BYBOX 400 400 km ASC COUNT 3 STOREDIST",
        },
    )
