from oldnyc.util import remove_empty


def test_remove_empty():
    assert remove_empty(
        {
            "alt_title": [],
            "subjects": {
                "geographic": ["Staten Island (New York, N.Y.)"],
                "name": [],
                "temporal": [],
                "topic": [],
            },
        }
    ) == {
        "subjects": {
            "geographic": ["Staten Island (New York, N.Y.)"],
        }
    }
