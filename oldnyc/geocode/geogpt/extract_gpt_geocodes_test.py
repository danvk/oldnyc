from geogpt.extract_gpt_geocodes import patch_query


def test_patch_query():
    assert (
        patch_query("4514 16th Avenue & 46th Street, Brooklyn, NY")
        == "16th Avenue & 46th Street, Brooklyn, NY"
    )
    assert (
        patch_query("131-135 Pitt St & E Houston St, Manhattan, NY")
        == "Pitt St & E Houston St, Manhattan, NY"
    )
    assert (
        patch_query("334-336 Atlantic Avenue, Brooklyn, NY") == "336 Atlantic Avenue, Brooklyn, NY"
    )


def test_do_not_patch_query():
    assert (
        patch_query("112 Schermerhorn Street, Brooklyn, NY")
        == "112 Schermerhorn Street, Brooklyn, NY"
    )
    assert (
        patch_query("18th Avenue & 75th Street, Brooklyn, NY")
        == "18th Avenue & 75th Street, Brooklyn, NY"
    )
