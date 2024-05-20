# ffssb

`ffssb` is a tool to create firefox site specific browser's. It turns any web
page into a desktop application with firefox.

It's similar in functionality to chrome's `Application shortcuts` or the [ssb feature](https://wiki.mozilla.org/Prism)
that existed in firefox, but [got removed](https://bugzilla.mozilla.org/show_bug.cgi?id=1682593).

Ssb allow to take advantage of that many common tools have competent web
versions. It makes it possible to avoid installing proprietary desktop apps (that
will usually run as a web based election apps anyway).

In linux it can sometimes be better supported since web versions seems to be
better maintained than the desktop alternatives.

Supports linux, tested on fedora with gnome.

## Getting started

### Install

The easiest way to get started:
``` sh
git clone https://github.com/sebastianappler/ffssb
make && make install
```

You can also specify an alternate Python binary:
``` sh
git clone https://github.com/sebastianappler/ffssb
PYTHON_BIN="$(which python3)" make && make install
```

Finally, it's also possible to run the python script directly:
``` sh
pip install -r requirements.txt
python ffssb.py <cmd>
```

### Create ssb

To create a ssb run:
``` sh
ffssb create hn https://news.ycombinator.com/ --display-name "Hacker News"
```

Then search for "Hacker News" in your applications (press Super-key, start
typing) and start it. Alternatively, launch the ssb from the command line
by typing:
``` sh
ffssb launch hn
```

To show more commands:
``` sh
ffssb --help
ffssb <cmd> --help
```

## How does it work

`ffssb` takes advantage of firefox profiles and the --no-remote flag in firefox
cli. When creating a new ssb it copies the current profile into a new one. Then
creates a desktop entry that can be started with the profile as a separate
instance. Because of this, it's safe to customize the ssb instance without
affecting other firefox profiles.

It also takes advantage of the user chrome feature to make it look cleaner
and more suitable as a stand-alone application. This can be disabled with the
--no-user-chrome flag.

## Q & A

### Why not just open a tab and drag it to a new window?
For programs that's used frequently it's easier to open them by name as a
separate app from the os.

It's also easier to switch between separated apps than to find it in a tab in a
browser window. Compare it to open an IDE as a browser tab or as it's own app.

## Known limitations

### Links
At the moment links in ssb will be opened inside the ssb instance. There's some
workarounds but it requires to install a client application check e.g
[External Application Button](https://addons.mozilla.org/en-US/firefox/addon/external-application/)
