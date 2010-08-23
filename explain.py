#!/usr/bin/env python
# coding: utf8

import sys
import textwrap
from optparse import OptionParser

def parse_plain_explanation(filename):
    # Read the file, remove newlines at the end of lines and only keep
    # relevant lines.
    with open(filename, 'r') as fp:
        content = fp.readlines()

    ignore_strings = ['#', ';', '!', '"']

    content = [i.strip('\n') for i in content]
    content = [i for i in content if i != '']
    content = [i for i in content if i[0] not in ignore_strings]

    indexed_comments = []
    cmd = content.pop(0)

    i = 0
    while i < len(content):
        # What range in the command does this comment belong to?
        start = content[i].count(' ')
        length = content[i].count('-')
        i += 1

        # Get the comment itself.  Every line with the same indentation
        # level is part of the comment.  However, remove any newlines
        # and indentation.
        comment = []
        while i < len(content) and \
              content[i].startswith(' ' * start) and \
              content[i][start] != ' ':
            comment += [content[i].strip()]
            i += 1

        indexed_comments += [(start, length, ' '.join(comment))]

    return (cmd, indexed_comments)

def explain(line_len, cmd, indexed_comments):
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
    if indexed_comments[-1][1] > 2:
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
    for start, length, _ in indexed_comments:
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
        (cmd, indexed_comments) = parse_plain_explanation(i)
        explained += [explain(options.width, cmd, indexed_comments)]

    print '\n'.join(explained),

# vim: set ts=4 sw=4 et :
