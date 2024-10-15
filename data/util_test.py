from data.util import clean_creator, clean_date, clean_title


def test_clean_title():
    assert (
        clean_title("Occupations - Peddlers - Clothing - Dresses.")
        == "Occupations - Peddlers - Clothing - Dresses."
    )
    assert (
        clean_title("Manhattan: 100th Street (West) - Amsterdam Avenue")
        == "Manhattan: 100th Street (West) - Amsterdam Avenue"
    )
    assert (
        clean_title("Feast of San Rocco [Saint Roch].")
        == "Feast of San Rocco [Saint Roch]."
    )
    assert (
        clean_title("[Manhattan: Cherry Street ; 128 Cherry Street.]")
        == "Manhattan: Cherry Street ; 128 Cherry Street."
    )
    assert (
        clean_title(
            "Bronx Kills - Bronx - [Freight yards of New York, New Haven and Hartford Railroad.]"
        )
        == "Bronx Kills - Bronx - [Freight yards of New York, New Haven and Hartford Railroad.]"
    )
    assert (
        clean_title("Avenue B at 13th Street and , to Northeast, Manhattan")
        == "Avenue B at 13th Street, to Northeast, Manhattan"
    )
    assert (
        clean_title(
            "Bridges - Hell Gate Bridge [New York Connecting Railroad Bridge - East River.]"
        )
        == "Bridges - Hell Gate Bridge [New York Connecting Railroad Bridge - East River.]"
    )


def test_clean_date():
    assert clean_date("[194-]") == "194-"
    assert clean_date("1933; 1936") == "1933, 1936"
    assert clean_date("1924, 1925, 1922") == "1922, 1924, 1925"
    assert clean_date("[ca. 1930]") == "1930"
    assert clean_date("ca. 1930") == "1930"
    assert clean_date("n.d") == ""
    assert clean_date("[Unknown]") == ""
    assert clean_date("1922?") == "1922"
    assert clean_date("1921; n.d") == "1921"
    assert clean_date("[ca. 1940?]") == "1940"

    assert clean_date("1937; July 1937") == "1937, 1937-07"
    assert clean_date("1947, Oct. 6") == "1947-10-06"
    assert clean_date("1 May 1937, 1937") == "1937, 1937-05-01"
    assert clean_date("1910, Febraury 24") == "1910-02-24"
    assert clean_date("1979, 21 October 1979") == "1979, 1979-10-21"
    assert clean_date("1979, 21October 1979") == "1979, 1979-10-21"
    assert clean_date("1910, February 24") == "1910-02-24"
    assert clean_date("1910-02-24") == "1910-02-24"
    assert clean_date("Febraury 24, 1910") == "1910-02-24"

    # assert clean_date("1849, 1871-1873") == "1849, 1871, 1873"


def test_clean_creator():
    assert (
        clean_creator("Sperr, Percy Loomis,1890-1964--Photographer")
        == "Sperr, Percy Loomis"
    )
    assert (
        clean_creator("New York (N.Y.). Tenement House Dept.--Photographer")
        == "New York (N.Y.). Tenement House Dept."
    )
    assert (
        clean_creator(
            "Van der Weyde, William M. (William Manley),1870-1928--Photographer"
        )
        == "Van der Weyde, William M. (William Manley)"
    )
    assert (
        clean_creator(
            "Chinn, George D.--Photographer;Sperr, Percy Loomis,1890-1964--Photographer"
        )
        == "Chinn, George D.; Sperr, Percy Loomis"
    )
    assert (
        clean_creator(
            "Sperr, Percy Loomis,1890-1964--Photographer\n\n\t\t\t\t\t\t\t\t\t\t\t\n\n\t\t\t\t\t\t\t\t\t\t \n\n\t\t\t\t\t\t\t\t\n\n\t\t\t\t\n\n\t\t\t\t\t\t\n\n\t\t\n\n\t\t\t\t\t\t\n\n\n\n\t\t\t\t\t\t\n\n\n\n\t\t\n\n\t\t\t\t\t\n\n\t\t\t\t\t\tErrors: The search index you specified could not be found. More information:;java.io.FileNotFoundException: /usr/local/www/digitalgallery.nypl.org/digital_gallery/alt_title_index/_1dq.frq (Too many open files)"
        )
        == "Sperr, Percy Loomis"
    )
