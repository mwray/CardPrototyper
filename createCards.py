#!/usr/bin/python
import os
import sys
import codecs
import svgwrite as sw
import numpy as np
from pprint import pprint

#paper sizes
sizes = {
    'a5':(148, 210),
    'a4':(210, 297),
    'a3':(297, 420),
    'letter':(216, 279),
    'half-letter':(140, 216),
    'legal':(216,356),
    'junior-legal':(127,203),
    'tabloid':(279,432)
}


def mm(val):
    '''converts float value into string format with mm'''
    if len(val) == 1:
        return str(val) + 'mm'
    else:
        return (str(val[0]) + 'mm', str(val[1]) + 'mm')


def cm(val):
    '''converts float value into string format with cm'''
    if len(val) == 1:
        return str(val / 10) + 'cm'
    else:
        return (str(val[0] / 10) + 'cm', str(val[1] / 10) + 'cm')


def split(string, delimiters):
    '''splits string with a number of different delimiters (inside a list)'''
    new_str = string.split(delimiters[0])
    for i in range(1,len(delimiters)):
        temp_list = []
        for j in new_str:
            temp_splits = j.split(delimiters[i])
            for k in range(0,len(temp_splits) - 1):
                temp_splits[k] += delimiters[i]
            for k in temp_splits:
                temp_list.append(k)
        new_str = temp_list
    return new_str


def print_help():
    '''prints help for the program'''
    print('USAGE: createCards.py [args] infile[s] [-o outfile]')
    print
    print('Arg list')
    print
    print('-h           : show help.')
    print('-b           : Bold headings.')
    print('-t           : Indent body text.')
    print('-s  size     : Specify the size of the output file.')
    print('-o  outfile  : Specify name of the output file.')
    print('-m  margin   : Specify the size of the margins.')
    print('-c  w h      : Specify the card height (h) and width (w).')
    print('-r size     : Specify size of rounded corners, 0 is none.')


def parse_args(args):
    '''parses the different args for the program, see the print_help function'''
    help_ = False
    in_files = []
    out_file = ''
    size_ = 'a4'
    style = {'bold':False, 'tab':False, 'newline':False}
    margin = 3.5
    card_size = (64, 88)
    corners = 4

    a = 1
    while a < len(args):
        if args[a] == '-h':
            help_ = True
        elif args[a] == '-o':
            a += 1
            out_file = args[a]
        elif args[a] == '-s':
            a += 1
            size_ = args[a]
        elif args[a] == '-b':
            style['bold'] = True
        elif args[a] == '-t':
            style['tab'] = True 
        elif args[a] == '-m':
            a += 1
            margin = float(args[a])
        elif args[a] == '-c':
            a += 1
            w = float(args[a])
            a += 1
            h = float(args[a])
            card_size = (w, h)
        elif args[a] == '-r':
            a += 1
            corners = float(args[a])
        else:
            in_files.append(args[a])
        a += 1
    if len(in_files) == 0 or help_:
        print_help()
        sys.exit()
    return (in_files, out_file, size_, style, margin, card_size, corners)


def get_file_name(f_name, num):
    '''appends num to f_name before the last '.' '''
    words = f_name.split('.')
    pre = '.'.join(words[0:-1])
    post = words[-1]
    return pre + str(num) + '.' + post


def read_csvs(in_files):
    '''reads and return csvs in the list inside in_files'''
    cards = [[]]
    for file_ in in_files:
        with codecs.open(file_, 'r', encoding="utf-8-sig") as in_f:
            for line in in_f:
                clean_line = line.lstrip().rstrip()
                words = clean_line.split(',')
                if words[0] == '':
                    cards.append([])
                    continue
                cards[-1].append((words[0],words[1]))
    return cards


def draw_hexagon(svg, pos, num, margin, y_c, filled):
    '''
    Write a hexagon to the svg with given position
    Write a group of 7 hexagons to the svg with given position.
    svg    -- The svgwrite object to write and save to.
    pos    -- The base position to write the text to.
    num    -- Which hexagon is begin drawn
    margin -- The margin on the card
    y_c    -- The line counter denoting the current position.
    filled -- Which hexagons are filled (and in what colour)
    '''
    ang = (num-1) * np.pi / 3;
    if num != 0:
        h_pos = (pos[0] + (10 * np.sin(ang)), pos[1] + (10 * np.cos(ang)))
    else:
        h_pos = pos
    if filled == 0:
        fill = 'white'
    elif filled == 1:
        fill = 'green'
    elif filled == 2:
        fill = 'red'
    elif filled == 3:
        fill = 'orange'
    else:
        fill = 'gray'
    h = sw.shapes.Circle(mm(h_pos), '5mm', fill=fill, stroke='black', stroke_width=2);
    svg.add(h)


def write_hexagons(svg, pos, margin, y_c, filled):
    '''
    Write a group of 7 hexagons to the svg with given position.
    svg    -- The svgwrite object to write and save to.
    pos    -- The base position to write the text to.
    margin -- The margin on the card
    y_c    -- The line counter denoting the current position.
    filled -- Which hexagons are filled (and in what colour)
    '''
    t_pos = (pos[0] + 10*3, pos[1] + (y_c * margin[1]) + 10*3)
    for h in range(7):
        draw_hexagon(svg, t_pos, h, margin, y_c, filled[h])


def write_line(svg, pos, margin, y_c, text, style, header):
    '''
    Write a line of text to the svg with given position and styles.

    Keyword arguments:
    svg    -- The svgwrite object to write and save to.
    pos    -- The base position to write the text to.
    margin -- The margin on the card
    y_c    -- The line counter denoting the current position.
    text   -- The text to write.
    style  -- The style of the text to print, see the parse_args function.
    header -- Whether or not the text is part of the header.
    '''
    #Work out position of text given margins
    t_pos = (pos[0] + margin[0], pos[1] + (y_c * margin[1]))
    text_style = ''
    #add styles
    if style['bold'] and header:
        text_style += ' font-weight:bold'
    if style['tab'] and not header:
        t_pos = (t_pos[0] + 2, t_pos[1])
    #write text
    if text_style == '':
        t = sw.text.Text(text, mm(t_pos))
    else:
        t = sw.text.Text(text, mm(t_pos), style=text_style)
    y_c += 1
    svg.add(t)
    return y_c


def convert_text(svg, pos, margin, y_c, text, char_width, card_size, style, header):
    '''
    Converts text input to multiple lines fitting inside a single card and then
    writes the shortened text to the svg.

    Keyword arguments:
    svg        -- The svgwrite object to write and save to.
    pos        -- The base position to write the text to.
    margin     -- The margin on the card
    y_c        -- The line counter denoting the current position.
    text       -- The text to write.
    char_width -- Approx. width of the characters so that it doesn't overlap.
    card_size  -- The size of the card currently writing to.
    style      -- The style of the text to print, see the parse_args function.
    header     -- Whether or not the text is part of the header.
    '''
    texts = []
    split_text = split(text, [' ', ':', ',', '.', '-'])
    i = 0
    curr_text = ''
    #Run through every piece of split text
    for i in range(len(split_text)):
        curr_length = len(curr_text)
        #check next lot of text won't cause an overlap, if it doesn't add it.
        if char_width * (len(split_text[i]) + curr_length + 1) < card_size[0] - 2 * margin[0]:
            curr_text += split_text[i] + ' '
        elif curr_text == '':
            #In this case one word might be too long for the card
            texts.append(str(curr_text))
            curr_text = split_text[i] + ' '
            print('WARNING: Text size may be too long for the card(s).')
        else:
            texts.append(str(curr_text))
            curr_text = split_text[i] + ' '
    if curr_text != '':
        texts.append(curr_text)

    #write all of the lines onto the svg
    for t in texts:
        y_c = write_line(svg, pos, margin, y_c, t, style, header)
    return y_c


def write_text(svg, pos, margin, y_c, text, card_size, style):
    '''
    writes text onto a card with the given style

    Keyword arguments:
    svg        -- The svgwrite object to write and save to.
    pos        -- The base position to write the text to.
    margin     -- The margin on the card
    y_c        -- The line counter denoting the current position.
    text       -- The text to write.
    card_size  -- The size of the card currently writing to.
    style      -- The style of the text to print, see the parse_args function.
    '''

    char_width = 2

    title = True
    #Check if the input is a bullet point
    if text[0][0] == '*' and text[0][1] == ' ':
        y_c = convert_text(svg, pos, margin, y_c, text[0]+':'+text[1], char_width, card_size, style, False)
        return y_c
    #Check if the header should be written
    if text[0][0] != '[':
        title = False
        y_c = convert_text(svg, pos, margin, y_c, text[0], char_width, card_size, style, True)
    y_c = convert_text(svg, pos, margin, y_c, text[1], char_width, card_size, style, title or False)
    return y_c


def create_cards(cards, out_file, paper_size, margin, card_size, style, corners):
    '''
    Creates cards from the dictionary given a number of paramters

    Keyword arguments:
    cards      -- Dict containing the text for each card.
    out_file   -- The name of the (first) output file.
    paper_size -- The size of the paper using (see paper sizes above).
    margin     -- The size of the margin that is being used.
    card_size  -- The size of the cards.
    style      -- The style of the text to print, see the parse_args function.
    corners    -- The size of the rounded corners (0 is a sharp corner).
    '''
    svg = sw.Drawing(filename=out_file, size=mm(paper_size), debug=True)
    svgs = [svg]
    x_c = 0
    y_c = 0
    #add margin size to card size
    size_ = (margin[0] + card_size[0], margin[1] + card_size[1])
    curr_page = 0
    #create grid of cards
    for c in cards:
        pos = (margin[0] + x_c * size_[0], margin[1] + y_c * size_[1])
        #Check if max horizontal, if so move onto next line
        if pos[0] + card_size[0] + 2 * margin[0] > paper_size[0]:
            x_c = 0
            y_c += 1
            pos = (margin[0] + x_c * size_[0], margin[1] + y_c * size_[1])
        #check if max vertical, if so move onto next file
        if pos[1] + card_size[1] + 2 * margin[1] > paper_size[1]:
            x_c = 0
            y_c = 0
            pos = (margin[0] + x_c * size_[0], margin[1] + y_c * size_[1])
            curr_page += 1
            svgs.append(sw.Drawing(filename=get_file_name(out_file,curr_page), size=mm(paper_size), debug=True))
        #Create basic rectangle for the card with/without corners.
        if corners > 0:
            r = sw.shapes.Rect(mm(pos), mm(card_size), corners, corners, fill='white', stroke='black', stroke_width=2)
        else:
            r = sw.shapes.Rect(mm(pos), mm(card_size), fill='white', stroke='black', stroke_width=2)
        svgs[curr_page].add(r)
        t_y_c = 1
        #write the text on the card
        for w in c:
            t_y_c = write_text(svgs[curr_page], pos, margin, t_y_c, w, card_size, style)
        write_hexagons(svgs[curr_page], pos, margin, t_y_c, [5,1,0,0,3,1,0])
        x_c += 1
    #save svgs
    for s in svgs:
        s.save()


if __name__ == '__main__':
    #Parse arguments
    args = parse_args(sys.argv)
    in_files = args[0]
    if args[2] not in sizes:
        raise error('Incorrect size inputted')
    size_ = sizes[args[2]]
    style = args[3]
    margin = (args[4], args[4])
    card_size = args[5]
    corners = args[6]
    if args[1] == '':
        out_file = 'out_cards.svg'
    else:
        out_file = args[1]
    #read csvs
    cards = read_csvs(in_files)
    #create cards
    create_cards(cards, out_file, size_, margin, card_size, style, corners)
