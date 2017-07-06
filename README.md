# Card Prototyper
Code for creating prototype cards for board games. Takes in a .csv and creates an svg file.

## Installation

Requires: 
* Python (2.7+ or 3.3+ earlier versions may work)
* svgwrite

1. Install python from [here](https://www.python.org/downloads/)
2. Install pip using [this](https://pip.pypa.io/en/stable/installing/) if required.
3. Install svgwrite by typing ``pip install svgwrite``

## Usage

USAGE: createCards.py [args] infile[s] [-o outfile]

Arg list

-h           : show help.

-b           : Bold headings.

-t           : Indent body text.

-s  size     : Specify the size of the output file.

-o  outfile  : Specify name of the output file.

-m  margin   : Specify the size of the margins.

-c  w h      : Specify the card height (h) and width (w).

-r size     : Specify size of rounded corners, 0 is none.


### Examples

* ``python createCards.py Test_cards.csv`` _creates a svg with default sizes_
* ``python createCards.py Test_cards.csv -o tc.svg -r 0`` Creates an svg called tc.svg with straight corners.
* ``python createCards.py Test_cards.csv -b -t`` Creates an svg with bold headings and indented text.

## CSV Format
The csv format is in two columns with the first column representing a header and the second a value.

Cards are separated by an empty row. 

If you wish the heading to be suppressed it can be wrapped in square brackets, _i.e._ [].

For example a playing card might look like this:

``[Suit],Hearts,``

``[Value],A,``

``,``

``[Suit],Hearts,``

``[Value],2,``

## Other Info

Feel free to suggest changes/create pull requests with more features. At the moment it is very basic, but hopefully it should get the job done!
