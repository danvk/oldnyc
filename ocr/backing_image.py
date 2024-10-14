#!/usr/bin/env python

from data.item import json_to_item


if __name__ == "__main__":
    rs = [json_to_item(line) for line in open("data/images.ndjson")]

    for r in rs:
        back_id = r.back_id
        if not back_id:
            continue
        # url = f"http://images.nypl.org/?id={back_id}&t=w"
        # print("%s\t%s.jpg" % (url, back_id))
        print(back_id)
