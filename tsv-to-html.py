#! /usr/bin/env python3
import sys

ENCODING="UTF-8"


def error(template, *args, **kwargs):
    print(template.format(*args, **kwargs), file=sys.stderr)


def usage(progname):
    error('\nUsage: {} INPUT OUTPUT\n', progname)
    error('\tINPUT is the filename of the input TSV file')
    error('\tOUTPUT is the filename of the output HTML file')


if len(sys.argv) != 3:
    usage(sys.argv[0])
    sys.exit(1)

with open(sys.argv[1], "rt", encoding=ENCODING) as lines:
    with open(sys.argv[2], "wt", encoding=ENCODING) as output:
        print('<html>', file=output)
        print('<head>', file=output)
        print('<meta http-equiv="Content-Type" value="text/html; charset=UTF-8">', file=output)
        print('</head>', file=output)
        print('<body>', file=output)
        print('<table>', file=output)
        for line in lines:
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            columns = line.rstrip().split('\t')
            print('<tr><td>' + '</td><td>'.join(columns) + "</td></tr>", file=output)
        print('</table>', file=output)
        print('</body>', file=output)
        print('</html>', file=output)

