from __future__ import absolute_import
from __future__ import print_function

import re
import io

INCLUDE_MATCHER = re.compile(
    '''^#\+INCLUDE: "(?P<path>.+?)"(?: :lines "(?P<start>\d+)?-(?P<stop>\d+)?")?$''',
    flags=re.MULTILINE
)


def recursive_include(f, doc_tree=None, start_line=None, stop_line=None):
    """
    Recursively read a markdown includes.

    Read markdown files, and recursively process the data into a StringIO
    object at each step.
    """
    # first of all, only include lines for processing per the start and
    # stop from any include
    data = f.readlines()
    markdown = ''.join(data[slice(start_line, stop_line)])

    # but storage for the incoming markdown
    included_content = {}

    for match in INCLUDE_MATCHER.finditer(markdown):
        gd = match.groupdict()
        input_file = io.open(gd['path'], 'r', encoding='utf-8')
        included_content[(match.start(), match.end())] = recursive_include(
            input_file,
            doc_tree,
            int(gd['start']) if gd['start'] else None,
            int(gd['stop']) if gd['stop'] else None
        )
        try:
            # Assume a networkx digraph, and add an edge from the current
            # file to the children
            doc_tree.add_edge(f.name, gd['path'])
        except AttributeError:
            pass

    # Go through the includes from the last through to the first, updating the
    # markdown data
    print(included_content)
    for start_stop in sorted(included_content, reverse=True):
        markdown = ''.join([
            markdown[:start_stop[0]],
            included_content[start_stop].read(),
            markdown[start_stop[1]:]
        ])

    return io.StringIO(markdown)
