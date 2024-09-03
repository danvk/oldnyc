import crawl.nypl_html


def test_extract_search():
    with open("crawl/testdata/search.html") as f:
        html = f.read()
        results = crawl.nypl_html.extract_results(html)
        assert results == [
            {
                "uuid": "510d47dd-af0d-a3d9-e040-e00a18064a99",
                "image_url": "https://images.nypl.org/index.php?id=734637F&t=f",
                "title": "North (Hudson) River - Pier 11.",
                "has_multiple": True,
                "photo_id": "734637f",
            }
        ]


def test_item1():
    with open("crawl/testdata/1508179.html") as f:
        html = f.read()
        item = crawl.nypl_html.extract_item(html)
    assert item == {
        "id": "1508179",
        "uuid": "510d47e2-00bb-a3d9-e040-e00a18064a99",
        "item": {
            "id": "510d47e2-00bb-a3d9-e040-e00a18064a99",
            "url": "/items/510d47e2-00bb-a3d9-e040-e00a18064a99",
            "thumb": "https://images.nypl.org/index.php?id=1508179&t=b",
            "src": "https://images.nypl.org/index.php?id=1508179&t=w",
            "title": "South Street - Broad Street - Coeuties Slip",
            "index": 0,
            "image_id": "1508179",
        },
        "sibling": {
            "id": "510d47e2-00bc-a3d9-e040-e00a18064a99",
            "url": "/items/510d47e2-00bc-a3d9-e040-e00a18064a99",
            "title": "South Street - Broad Street - Coeuties Slip",
            "image_id": "1508180",
            "parentUUID": [
                "63401f40-c5ce-012f-d426-58d385a7bc34",
                "c7ca7190-c5cd-012f-e3d5-58d385a7bc34",
                "8a2e2e90-c5cd-012f-9f4e-58d385a7bc34",
            ],
            "iiif": False,
            "multi": True,
            "index": 1,
            "high_res_link": None,
            "title_full": "South Street - Broad Street - Coeuties Slip",
        },
        "meta": {
            "place": "New York, NY.",
            "date_created": "1921-05-06",
            "topics": [
                "New York (N.Y.)",
                "New York (N.Y.) -- Buildings, structures, etc.",
            ],
            "genre": "Photographs",
            "resource_type": "Still image",
            "rlin_oclc": "62279538",
            "bnumber": "b16177190",
            "uuid": "63401f40-c5ce-012f-d426-58d385a7bc34",
        },
    }


def test_item2():
    with open("crawl/testdata/1508745.html") as f:
        html = f.read()
        item = crawl.nypl_html.extract_item(html)
    assert item == {
        "id": "1508745",
        "uuid": "510d47e2-01a5-a3d9-e040-e00a18064a99",
        "item": {
            "id": "510d47e2-01a5-a3d9-e040-e00a18064a99",
            "url": "/items/510d47e2-01a5-a3d9-e040-e00a18064a99",
            "thumb": "https://images.nypl.org/index.php?id=1508745&t=b",
            "src": "https://images.nypl.org/index.php?id=1508745&t=w",
            "title": "Fifth Avenue - 33rd Street - 34th Street, looking south",
            "index": 0,
            "image_id": "1508745",
        },
        "sibling": {
            "id": "510d47e2-01a6-a3d9-e040-e00a18064a99",
            "url": "/items/510d47e2-01a6-a3d9-e040-e00a18064a99",
            "title": "Fifth Avenue - 33rd Street - 34th Street, looking south",
            "image_id": "1508746",
            "parentUUID": [
                "8b4540e0-c5ce-012f-08d7-58d385a7bc34",
                "c7ca7190-c5cd-012f-e3d5-58d385a7bc34",
                "8a2e2e90-c5cd-012f-9f4e-58d385a7bc34",
            ],
            "iiif": False,
            "multi": True,
            "index": 1,
            "high_res_link": None,
            "title_full": "Fifth Avenue - 33rd Street - 34th Street, looking south",
        },
        "meta": {
            "alt_title": "Empire State Building",
            "place": "New York, NY.",
            "date_created": "1983",
            "topics": [
                "New York (N.Y.)",
                "New York (N.Y.) -- Buildings, structures, etc.",
                "Empire State Building (New York, N.Y.)",
            ],
            "genre": "Photographs",
            "resource_type": "Still image",
            "rlin_oclc": "62279538",
            "bnumber": "b16177190",
            "uuid": "8b4540e0-c5ce-012f-08d7-58d385a7bc34",
        },
    }
