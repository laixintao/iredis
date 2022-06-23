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
