#!/usr/bin/python
#
# Simple hosttag client
# 
# Usage:
#   ht <tag>
#
#   ht [-a] <tag1> <tag2>           Show hosts with tag1 AND tag2 (intersection, default)
#   ht -o <tag1> <tag2>             Show hosts with tag1 OR tags2 (union)
#
#   ht -t                           Show all tags
#   ht -t <host>                    Show tags on 'host'
#   ht -t [-o] <host1> <host2>      Show tags on 'host' OR 'host2' (union, default)
#   ht -t -a <host1> <host2>        Show tags on 'host' AND 'host2' (intersection)
#

hosttag_baseurl = 'http://hosttag:1980/'

import getopt, sys
import urllib2


def usage():
    print 'usage: ' + sys.argv[0] + "    [-a|-o] <tag1>    [<tag2>]  (default if multiple tags is AND)";
    print '       ' + sys.argv[0] + " -t [-a|-o] [<host1>] [<host2>] (default if multiple hosts is OR)";

try:
    opts, args = getopt.getopt(sys.argv[1:], '?Aaohtv', [ 'help', 'all', 'and', 'or', 'tag', 'host', 'noop', 'verbose' ])
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

arg_type = { 'host': 'tag', 'tag': 'host' }
rel = None
all = 0
noop = 0
verbose = 0
mode = None
for o, a in opts:
    if o in ('-?', '--help'):
        usage()
        sys.exit(0)
    elif o in ('-A', '--all'):
        all += 1
    elif o in ('-a', '--and'):
        rel = 'and'
    elif o in ('-o', '--or'):
        rel = 'or'
    # -h and --host are now deprecated, and at some point will be removed
    elif o in ('-t', '--tag', '-h', '--host'):
        mode = 'tag'
    elif o in ('-v', '--verbose'):
        verbose = 1
    elif o in ('--noop'):
        noop = 1
    else:
        usage()
        assert False, 'unhandled option'

# Report all hosts with -A
if all:
    args = [ 'ALL' ]
elif mode == 'tag' and len(args) < 1:
    args = [ 'ALL' ]

if not mode:
    mode = 'host'
if mode == 'host' and all > 1:
    args = [ 'ALL_SKIP' ]

if len(args) < 1:
    usage()
    sys.exit(2)

if len(args) > 1 and rel == None:
    if mode == 'host':
        rel = 'and'
    else:
        rel = 'or'

if verbose and rel:
    print >> sys.stderr, '+ rel: ' + rel

# Fetch data
d = ()
for arg in args:
    if mode == 'tag':
        namespace = 'hosts'
    else:
        namespace = 'tags'
    url = '%s%s/%s' % ( hosttag_baseurl, namespace, arg )
    if verbose:
        print >> sys.stderr, '+ url: ' + url

    if noop:
        continue

    usock = None
    try:
        usock = urllib2.urlopen( url )
    except urllib2.HTTPError, err:
        if err.code == 404:
            print >> sys.stderr, 'Error: ' + arg_type[mode] + " '" + arg + "' not found."
        else:
            print >> sys.stderr, err
        sys.exit(1)
    data = usock.read()
    usock.close()
    data = data.rstrip()

    # Special case single-arg request
    if len(args) == 1:
        print data
        sys.exit(0)

    if rel == 'list':
        print '%s: %s' % ( arg, data )
        continue

    if not len(d):
        d = set( data.split(' ') )
        continue

    if rel == 'and':
        d = d.intersection( set( data.split(' ') ) )
    elif rel == 'or':
        d = d.union( set( data.split(' ') ) )

if len(d):
    print ' '.join(sorted(d))


# vim:sw=4