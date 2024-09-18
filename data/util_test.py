from data.util import clean_date, clean_title


def test_clean_title():
    assert (
        clean_title("Occupations - Peddlers - Clothing - Dresses.")
        == "Occupations - Peddlers - Clothing - Dresses"
    )
    assert (
        clean_title("Manhattan: 100th Street (West) - Amsterdam Avenue")
        == "Manhattan: 100th Street (West) - Amsterdam Avenue"
    )
    assert (
        clean_title("Feast of San Rocco [Saint Roch].")
        == "Feast of San Rocco [Saint Roch]"
    )
    assert (
        clean_title("[Manhattan: Cherry Street ; 128 Cherry Street.]")
        == "Manhattan: Cherry Street ; 128 Cherry Street"
    )
    assert (
        clean_title(
            "Bronx Kills - Bronx - [Freight yards of New York, New Haven and Hartford Railroad.]"
        )
        == "Bronx Kills - Bronx - Freight yards of New York, New Haven and Hartford Railroad"
    )
    assert (
        clean_title("Avenue B at 13th Street and , to Northeast, Manhattan")
        == "Avenue B at 13th Street, to Northeast, Manhattan"
    )


def test_clean_date():
    assert clean_date("[194-]") == "194-"
    assert clean_date("1933; 1936") == "1933, 1936"
    assert clean_date("1924, 1925, 1922") == "1922, 1924, 1925"
    assert clean_date("[ca. 1930]") == "1930"
    assert clean_date("n.d") == ""
    assert clean_date("[Unknown]") == ""
    assert clean_date("1922?") == "1922"
    assert clean_date("1921; n.d") == "1921"
    assert clean_date("[ca. 1940?]") == "1940"

    # assert clean_date("1937; July 1937") == "1937-07, 1937"
