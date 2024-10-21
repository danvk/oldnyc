Old NYC
=======

Live site: https://www.oldnyc.org

The static content for this site lives in [oldnyc/oldnyc.github.io][1].
In particular you may be interested in the [giant JSON data file][2] which contains all
the data served on the site.

This repo contains Python code used to generate the data for the site.

To get going on development:

```bash
git clone git://github.com/danvk/oldnyc.git
cd oldnyc
poetry install
```

See [howto.md](howto.md) for more details on how to perform specific tasks.

If you're interested in building your own "Old" site using this code, check out [this great writeup][3] on Old Ravenna.

[1]: https://github.com/oldnyc/oldnyc.github.io/
[2]: https://github.com/oldnyc/oldnyc.github.io/blob/master/data.json
[3]: http://www.opendatabassaromagna.it/2016/07/how-to-map-photos-of-your-city-like.html
