class BoxLine(object):
    def __init__(self, letter, left, top, right, bottom, page):
        self.letter = letter
        self.left = int(left)
        self.top = int(top)
        self.right = int(right)
        self.bottom = int(bottom)
        self.page = int(page)

    @staticmethod
    def parse_line(line):
        letter, left, bottom, right, top, page = line.split(' ')
        return BoxLine(letter, left, top, right, bottom, page)

    def __repr__(self):
        return ' '.join(str(x) for x in [
            self.letter,
            self.left,
            self.bottom,
            self.right,
            self.top,
            self.page])


def load_box_file(path):
    """Load the box data in the file at path.

    Output is a list of BoxLines.
    """
    out = []
    for line in open(path):
        out.append(BoxLine.parse_line(line))
    return out

