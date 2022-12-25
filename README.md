# Ingress Max Field Planner

This is a tool to create a PDF plan for a group of portals, yielding the maximum number of fields while minimizing the number of SoftBank Ultra Links and roughly the amount of time spent acquiring keys.


## Installation

Dependencies:
 - Python 3
 - A LaTeX installation (`pdflatex` command)
 - ImageMagick (`convert` command)
 - IITC extension installed ([Chrome](https://chrome.google.com/webstore/detail/iitc-button/febaefghpimpenpigafpolgljcfkeakn?hl=en), [Firefox](https://addons.mozilla.org/en-CA/firefox/addon/iitc-button/))
 - [Fanfields 2](https://github.com/Heistergand/fanfields2/raw/master/iitc_plugin_fanfields2.user.js) installed with IITC, which in turn needs Draw Tools enabled

## Usage

As with Fanfields2, on IITC, select some portals using the polygon option in Draw Tools. Enable the Fanfields2 layers and then run `grab.js` in the Developer Console, which will download `points.csv`.

Run `maxfield.py` using the following arguments:
```
python3 maxfield.py [filename] [-n trials]
```

Where `filename` is the location of the downloaded `points.csv` and `trials` is the number of attempts the program will make to find the least costly plan.

## Output

The program is guaranteed to find the maximum number of fields, and attempts to find the minimum number of SoftBank Ultra Links required, then the minimum amount of hacking required.

MU maximizing is still an open problem and no guarantees are made about MU.