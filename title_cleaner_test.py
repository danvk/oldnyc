import title_cleaner

TRUTH = [
    (True, 'Manhattan: 1st Ave. - 34th St. E.'),
    (True, 'Queens: Hoyt Avenue - 24th Street'),
    (False, "Queens: Flushing Meadow Park - New York World's Fair of 1939-40 - [Industrial exhibits.]"),
    (False, 'Fifth Avenue - 90th Street, southeast corner'),
    (False, 'Recreation and hobbies - Miscellaneous - Children.'),
    (True,  'Manhattan: 59th Street - 6th Avenue'),
    (True,  'Queens: Queens Boulevard - Junction Boulevard'),
    (True,  'Manhattan: 50th Street (West) - 5th Avenue'),
    (True,  'Manhattan: 5th Avenue - 78th Street'),
    (True,  'Manhattan: 5th Avenue - 33rd Street'),
    (True,  'Queens: Queens Boulevard - 62nd Avenue'),
    (False, 'Manhattan: Battery Park.'),
    (False, 'Manhattan: Central Park - The Sailboat Pool'),
    (True, 'Queens: Colonial Avenue - 62nd Drive'),
    (True, 'Queens: Woodhaven Blvd - Fleet Street'),
    (True, 'Richmond: New Dorp Lane - Cedar Grove Avenue')
]

def test_clean_title():
    for correct, title in TRUTH:
        assert correct == title_cleaner.is_pure_location(title), '%s %s' % (correct, title)
