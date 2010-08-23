#!/usr/bin/env python
# coding: utf8

import sys
import textwrap
from optparse import OptionParser

def parse_plaintext_explanation(filename):
    """Read the file and find out which ranges the comments apply to."""

    # Read the file, remove newlines at the end of lines and only keep
    # relevant lines.
    with open(filename, 'r') as fp:
        content = fp.readlines()

    ignore = ['#', ';', '!', '"']

    content = [i.strip('\n') for i in content]
    content = [i for i in content if len(i) == 0 or i[0] not in ignore]
    content += ['']

    # The command itself is in the very first line.
    cmd = content.pop(0).decode('UTF-8')

    # Read the markers and store their ranges.
    markers = content.pop(0) + ' '
    indexes = []
    start = -1
    i = 0
    for i in range(len(markers)):
        c = markers[i]
        if c == '-' and start == -1:
            start = i
        elif c == ' ' and start != -1:
            indexes += [(start, i - start)]
            start = -1
        elif c == '+' and start != -1:
            indexes += [(start, i - start + 1)]
            start = -1
        elif c == '!':
            indexes += [(i, 0)]
            start = -1

    # Extract comments.
    comments = []
    one_comment = []
    for line in content:
        if line == '' and len(one_comment) > 0:
            one_comment = ' '.join(one_comment)
            one_comment = one_comment.replace('\n', ' ')
            one_comment = one_comment.strip()

            comments += [one_comment.decode('UTF-8')]
            one_comment = []

        elif line != '':
            one_comment += [line]

    # Associate comments with their ranges.
    indexed_comments = zip(indexes, comments)
    indexed_comments = map(lambda ((start, length), comment):
            (start, length, comment), indexed_comments)
    indexed_comments.reverse()
    return (cmd, indexed_comments)

def explain(line_len, cmd, indexed_comments):
    """Given the desired line length, a command and a list of indexed
    comments, explain the command by drawing lines from the comments to
    the associated parts of the command.
    """

    # We *need* the lines to be at least as long as the command.
    # Additionally, add some space to the right which is needed for the
    # comments.
    line_len = max(line_len, len(cmd) + 10)

    # Our "drawing" will start with an initial empty line.
    empty_line = ' ' * line_len
    drawing = empty_line + '\n'
    y = 1

    # If the comment on the very right is associated with a range
    # greater than 2, then add an additional empty line.  This is done
    # because we want to show a "|" over each corner.  If we didn't add
    # the extra line, the "|" would be missing.
    if indexed_comments[0][1] > 2:
        drawing += empty_line + '\n'
        y += 1

    # Add the corner symbol and the wrapped comment.  Keep track of
    # where we placed the corners.  Every line will be exactly
    # "line_len" characters long.  This allows us to draw arrows and
    # stuff later on.
    corners = []
    for i in range(len(indexed_comments)):
        (start, length, comment) = indexed_comments[i]

        # The indented corner.
        first_indent = ' ' * start
        first_indent += ' ' * (length / 2)
        first_indent += '\\- '
        drawing += first_indent
        y += 1

        # Remember this corner.
        corners += [(start + length / 2, y)]

        # Wrap the comment and add its first line.
        comment_width = line_len - start - length / 2 - 3
        wrapped = textwrap.wrap(comment, comment_width)
        drawing += wrapped.pop(0).ljust(comment_width) + '\n'

        # Add remaining lines.  All of them have to be properly indented.
        for line in wrapped:
            drawing += ' ' * (start + length / 2 + 3)
            drawing += line.ljust(comment_width)
            drawing += '\n'
            y += 1

        # If this is not the very last comment, then add an extra line.
        if i < len(indexed_comments) - 1:
            drawing += empty_line + '\n'
            y += 1

    # Draw the lines from the corners up to the command.
    drawing_list = list(drawing)
    for x, y in corners:
        for i in range(y - 1):
            drawing_list[i * (line_len + 1) + x] = '|'

    # Draw ranges if they're greater 2.
    for (start, length, _) in indexed_comments:
        if length < 3:
            continue

        drawing_list[start] = '\\'
        drawing_list[start + length - 1] = '/'

        for i in range(start + 1, start + length - 1):
            drawing_list[i] = '-'

    # Convert it back to a string.
    drawing = ''.join(drawing_list)
    explained = cmd + '\n' + drawing

    # Remove any padding on the right hand.
    lines = explained.split('\n')
    lines = [i.rstrip() for i in lines]
    explained = '\n'.join(lines)
    return explained


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] file...")
    parser.add_option("-w", "--width", dest="width",
                      help="Maximum width of output",
                      default=72, type="int",
                      metavar="FILE")

    (options, args) = parser.parse_args()

    explained = []
    for i in args:
        (cmd, indexed_comments) = parse_plaintext_explanation(i)
        explained += [explain(options.width, cmd, indexed_comments)]

    print '\n'.join(explained),

# vim: set ts=4 sw=4 et :
