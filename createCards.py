import os, sys
import codecs
import svgwrite as sw
from pprint import pprint

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
    if len(val) == 1:
        return str(val) + 'mm'
    else:
        return (str(val[0]) + 'mm', str(val[1]) + 'mm')


def cm(val):
    if len(val) == 1:
        return str(val / 10) + 'cm'
    else:
        return (str(val[0] / 10) + 'cm', str(val[1] / 10) + 'cm')


def print_help():
    print 'USAGE: createCards.py [args] infile[s] [-o outfile]'
    print
    print 'Arg list'
    print
    print '-h           : show help.'
    print '-b           : Bold headings.'
    print '-t           : Indent body text.'
    print '-s  size     : Specify the size of the output file.'
    print '-o  outfile  : Specify name of the output file.'
    print '-m  margin   : Specify the size of the margins.'
    print '-c  w h      : Specify the card height (h) and width (w).'
    print '-r size     : Specify size of rounded corners, 0 is none.'


def parse_args(args):
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


def read_csvs(in_files):
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


#type_: 0 is normal, 1 is bolded, 2 is tab
def write_line(svg, pos, margin, y_c, text, style, header):
    t_pos = (pos[0] + margin[0], pos[1] + (y_c * margin[1]))
    text_style = ''
    if style['bold'] and header:
        text_style += ' font-weight:bold'
    if style['tab'] and not header:
        t_pos = (t_pos[0] + 2, t_pos[1])
    if text_style == '':
        t = sw.text.Text(text, mm(t_pos))
    else:
        t = sw.text.Text(text, mm(t_pos), style=text_style)
    y_c += 1
    svg.add(t)
    return y_c


#type_: 0 is normal, 1 is bolded, 2 is tab
def convert_text(svg, pos, margin, y_c, text, char_width, card_size, style, header):
    texts = []
    split_text = text.split(' ')
    i = 0
    curr_text = ''
    for i in range(len(split_text)):
        curr_length = len(curr_text)
        if char_width * (len(split_text[i]) + curr_length + 1) < card_size[0] - 2 * margin[0]:
            curr_text += split_text[i] + ' '
        elif curr_text == '':
            texts.append(str(curr_text))
            curr_text = split_text[i] + ' '
            print 'WARNING: Text size may be too long for the card(s).'
        else:
            texts.append(str(curr_text))
            curr_text = split_text[i] + ' '
    if curr_text != '':
        texts.append(curr_text)

    for t in texts:
        y_c = write_line(svg, pos, margin, y_c, t, style, header)
    return y_c


#type_: 0 is normal, 1 is bolded, 2 is bolded with tab
def write_text(svg, pos, margin, y_c, text, card_size, style):
    char_width = 2

    #if type_ == 0:
    #    if text[0][0] != '[':
    #        y_c = convert_text(svg, pos, margin, y_c, text[0] + ':' + text[1], char_width, card_size, style)
    #    else:
    #        y_c = convert_text(svg, pos, margin, y_c, text[1], char_width, card_size, style)
    #else:
    title = True
    if text[0][0] != '[':
        title = False
        y_c = convert_text(svg, pos, margin, y_c, text[0], char_width, card_size, style, True)
    y_c = convert_text(svg, pos, margin, y_c, text[1], char_width, card_size, style, title or False)
    return y_c


def create_cards(cards, out_file, paper_size, margin, card_size, style, corners):
    svg = sw.Drawing(filename=out_file, size=mm(paper_size), debug=True)
    x_c = 0
    y_c = 0
    size_ = (margin[0] + card_size[0], margin[1] + card_size[1])
    for c in cards:
        pos = (margin[0] + x_c * size_[0], margin[1] + y_c * size_[1])
        if pos[0] + card_size[0] + 2 * margin[0] > paper_size[0] or pos[1] > paper_size[1]:
            x_c = 0
            y_c += 1
            pos = (margin[0] + x_c * size_[0], margin[1] + y_c * size_[1])
        if corners > 0:
            r = sw.shapes.Rect(mm(pos), mm(card_size), corners, corners, fill='white', stroke='black', stroke_width=2)
        else:
            r = sw.shapes.Rect(mm(pos), mm(card_size), fill='white', stroke='black', stroke_width=2)
        svg.add(r)
        t_y_c = 1
        for w in c:
            t_y_c = write_text(svg, pos, margin, t_y_c, w, card_size, style)
        x_c += 1
    svg.save()


if __name__ == '__main__':
    args = parse_args(sys.argv)
    print args
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
    cards = read_csvs(in_files)
    create_cards(cards, out_file, size_, margin, card_size, style, corners)
