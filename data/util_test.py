from data.util import clean_title


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
