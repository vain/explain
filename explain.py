#!/usr/bin/env python
# coding: utf8

# ------------------------------------------------------------------
# "THE PIZZA-WARE LICENSE" (Revision 42):
# Peter Hofmann <pcode@uninformativ.de> wrote this file. As long as you
# retain this notice you can do whatever you want with this stuff. If
# we meet some day, and you think this stuff is worth it, you can buy
# me a pizza in return.
# ------------------------------------------------------------------

import sys
import textwrap
from optparse import OptionParser

def parse_plaintext_explanation(content):
    """Find out which ranges the comments apply to.

    Returns a list of tuples.  Each tuple contains one command and the
    list of associated comments (including the range for each comment).
    """

    # Split and filter lines.  The last empty line ensures that the end
    # of the last comment will be detected.
    lines = content.split('\n')
    lines = [i for i in lines if len(i) == 0 or i[0] != ';']
    lines += ['']

    all_explanations = []
    while len(lines) > 0:
        # The command itself is in the very first line.
        cmd = lines.pop(0)
        if cmd == '':
            continue

        # Read the markers and store their ranges.
        markers = lines.pop(0) + ' '
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
                if start != -1:
                    indexes += [(start, i - start)]
                indexes += [(i, 0)]
                start = -1

        # Extract comments.
        comments = []
        one_comment = []
        at = 0
        while len(lines) > 0 and at < len(indexes):
            line = lines.pop(0).strip()
            if line == '' and len(one_comment) > 0:
                one_comment = ' '.join(one_comment)
                comments += [one_comment]
                one_comment = []
                at += 1

            elif line != '':
                one_comment += [line]

        # No comments or no indices were found.
        if len(comments) == 0:
            all_explanations += [(cmd, None)]
            continue

        # Associate comments with their ranges.
        indexed_comments = zip(indexes, comments)
        indexed_comments = map(lambda ((start, length), comment):
                (start, length, comment), indexed_comments)
        indexed_comments.reverse()

        all_explanations += [(cmd, indexed_comments)]

    return all_explanations

def explain(options, cmd, indexed_comments):
    """Explain one single command.

    Given the desired options, a command and a list of indexed comments,
    explain the command by drawing lines from the comments to the
    associated parts of the command.  Line length and symbols for the
    graph are stored in "options".

    Returns the annotated command as a string.
    """

    if indexed_comments is None:
        return cmd + '\n'

    line_len = options.line_len
    corner = options.corner.decode('UTF-8')
    straight = options.straight.decode('UTF-8')
    ranges = options.ranges.decode('UTF-8')
    joints = options.joints.decode('UTF-8')

    if options.unicode_preset:
        corner = u'└ '
        straight = u'│'
        ranges = u'└─┘'
        joints = u'┬'

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

        # Don't move the graph to the right if length is too short.
        skip = 0
        if length >= 3:
            skip = length / 2

        # The indented corner.
        first_indent = ' ' * start
        first_indent += ' ' * skip
        first_indent += corner
        drawing += first_indent
        y += 1

        # Remember this corner.
        corners += [(start + skip, y)]

        # Wrap the comment and add its first line.
        comment_width = line_len - start - skip - len(corner)
        wrapped = textwrap.wrap(comment, comment_width)
        drawing += wrapped.pop(0).ljust(comment_width) + '\n'

        # Add remaining lines.  All of them have to be properly indented.
        for line in wrapped:
            drawing += ' ' * (start + skip + len(corner))
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
            drawing_list[i * (line_len + 1) + x] = straight

    # Draw ranges if they're greater 2.
    for (start, length, _) in indexed_comments:
        if length < 3:
            continue

        drawing_list[start] = ranges[0]
        drawing_list[start + length - 1] = ranges[2]

        for i in range(start + 1, start + length - 1):
            drawing_list[i] = ranges[1]

        drawing_list[start + length / 2] = joints

    # Convert it back to a string.
    drawing = ''.join(drawing_list)
    explained = cmd + '\n' + drawing

    # Remove any padding on the right hand.
    lines = explained.split('\n')
    lines = [i.rstrip() for i in lines]
    explained = '\n'.join(lines)
    return explained


if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [options] [file]...')
    parser.add_option('-w', '--width', dest='line_len',
                      help='Maximum width of output. Defaults to ' +
                      '%default.',
                      default=72, type='int')
    parser.add_option('-c', '--corners', dest='corner',
                      help='Characters to use as corners. Defaults ' +
                      'to "%default".', default='\\- ')
    parser.add_option('-s', '--straight', dest='straight',
                      help='Character to use as straight lines. ' +
                      'Defaults to "%default".', default='|')
    parser.add_option('-r', '--ranges', dest='ranges',
                      help='Characters to use for ranges. Defaults ' +
                      'to "%default".', default='\\_/')
    parser.add_option('-j', '--joints', dest='joints',
                      help='Character to use for joints between ' +
                      'lines and ranges. Defaults to "%default".',
                      default='_')
    parser.add_option('-u', '--unicode', dest='unicode_preset',
                      help='Use a preset of unicode glyphs for the graph.',
                      default=False, action='store_true')
    parser.add_option('-8', '--dont-force-utf-8', dest='force_utf8',
                      help='Do not enforce UTF-8 as output encoding.',
                      default=True, action='store_false')

    (options, args) = parser.parse_args()

    # Read all files or stdin.
    content = ''
    if len(args) > 0:
        for i in args:
            try:
                with open(i, 'r') as fp:
                    # Ensure that the last line ends with a newline.
                    # Also, an empty separating line is added.  This is
                    # necessary because we need at least one empty line
                    # between two files.
                    content += fp.read().decode('UTF-8') + '\n\n'
            except IOError as (errno, strerror):
                print >> sys.stderr, 'Can\'t read %s: %s' % (i, strerror)
                sys.exit(1)
    else:
        try:
            # No need to add anything here since there's *only* stdin
            # and no other files.
            content += sys.stdin.read().decode('UTF-8')
        except KeyboardInterrupt:
            sys.exit(1)

    # Annotate commands.
    parsed_lines = parse_plaintext_explanation(content)
    explained = []
    for (cmd, indexed_comments) in parsed_lines:
        explained += [explain(options, cmd, indexed_comments)]
    explained = '\n'.join(explained)

    # Enforce UTF-8?  This is needed when piping the output to another
    # program.  Can be turned off, though.
    if options.force_utf8:
        print explained.encode('UTF-8'),
    else:
        print explained,

# vim: set ts=4 sw=4 et :
