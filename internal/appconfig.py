# set global variables

import csv
import solr
from os import path, popen
from copy import deepcopy

from cspace_django_site import settings
from common import cspace  # we use the config file reading function


def getParms(parmFile):
    try:
        f = open(parmFile, 'rb')
        csvfile = csv.reader(f, delimiter="\t")
    except IOError:
        raise
        message = 'Expected to be able to read %s, but it was not found or unreadable' % parmFile
        return message, -1
    except:
        raise

    try:
        rows = []
        for row, values in enumerate(csvfile):
            rows.append(values)

        f.close()

        return parseRows(rows)

    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % parmFile
        return message, -1
    except:
        raise


def parseRows(rows):
    PARMS = {}
    HEADER = {}
    labels = {}
    FIELDS = {}
    DEFAULTSORTKEY = 'None'

    SEARCHCOLUMNS = 0
    SEARCHROWS = 0

    functions = 'Search,Facet,bMapper,listDisplay,fullDisplay,gridDisplay,inCSV'.split(',')
    for function in functions:
        FIELDS[function] = []

    fieldkeys = 'label fieldtype suggestions solrfield name X order'.split(' ')

    for rowid, row in enumerate(rows):
        rowtype = row[0]

        if rowtype == 'header':
            for i, r in enumerate(row):
                HEADER[i] = r
                labels[r] = i

        elif rowtype == 'server':
            SOLRSERVER = row[1]

        elif rowtype == 'core':
            SOLRCORE = row[1]

        elif rowtype == 'title':
            TITLE = row[1]

        elif rowtype == 'field':
            needed = [row[labels[i]] for i in 'Label Role Suggestions SolrField Name Search'.split(' ')]
            if row[labels['Suggestions']] != '':
                # suggestname = '%s.%s' % (row[labels['Suggestions']], row[labels['Name']])
                suggestname = row[labels['Name']]
            else:
                suggestname = row[labels['Name']]
            needed[4] = suggestname
            PARMS[suggestname] = needed
            needed.append(rowid)
            if 'sortkey' in row[labels['Role']]:
                DEFAULTSORTKEY = row[labels['SolrField']]

            for function in functions:
                if len(row) > labels[function] and row[labels[function]] != '':
                    fieldhash = {}
                    for n, v in enumerate(needed):
                        if n == 5 and function == 'Search':  # 5th item in needed is search field x,y coord for layout
                            if v == '':
                                continue
                            searchlayout = (v + ',1').split(',')
                            fieldhash['column'] = int('0' + searchlayout[1])
                            fieldhash['row'] = int('0' + searchlayout[0])
                            SEARCHCOLUMNS = max(SEARCHCOLUMNS, int('0' + searchlayout[1]))
                            SEARCHROWS = max(SEARCHROWS, int('0' + searchlayout[0]))
                        else:
                            fieldhash[fieldkeys[n]] = v
                    fieldhash['style'] = 'width:200px'  # temporary hack!
                    fieldhash['type'] = 'text'  # temporary hack!
                    FIELDS[function].append(fieldhash)

    if SEARCHROWS == 0: SEARCHROWS = 1
    if SEARCHCOLUMNS == 0: SEARCHCOLUMNS = 1

    return FIELDS, PARMS, SEARCHCOLUMNS, SEARCHROWS, SOLRSERVER, SOLRCORE, TITLE, DEFAULTSORTKEY


def loadConfiguration(configFileName):
    print configFileName
    config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), configFileName)


    try:
        DERIVATIVEGRID = config.get('internal', 'DERIVATIVEGRID')
        DERIVATIVECOMPACT = config.get('internal', 'DERIVATIVECOMPACT')
        SIZEGRID = config.get('internal', 'SIZEGRID')
        SIZECOMPACT = config.get('internal', 'SIZECOMPACT')
    except:
        print 'could not get image layout (size and derviative to use) from config file, using defaults'
        DERIVATIVEGRID     = "Thumbnail"
        DERIVATIVECOMPACT  = "Thumbnail"
        SIZEGRID           = "100px"
        SIZECOMPACT        = "100px"

    try:
        MAXMARKERS = int(config.get('internal', 'MAXMARKERS'))
        MAXRESULTS = int(config.get('internal', 'MAXRESULTS'))
        MAXLONGRESULTS = int(config.get('internal', 'MAXLONGRESULTS'))
        MAXFACETS = int(config.get('internal', 'MAXFACETS'))
        EMAILABLEURL = config.get('internal', 'EMAILABLEURL')
        IMAGESERVER = config.get('internal', 'IMAGESERVER')
        CSPACESERVER = config.get('internal', 'CSPACESERVER')
        INSTITUTION = config.get('internal', 'INSTITUTION')
        BMAPPERSERVER = config.get('internal', 'BMAPPERSERVER')
        BMAPPERDIR = config.get('internal', 'BMAPPERDIR')
        BMAPPERCONFIGFILE = config.get('internal', 'BMAPPERCONFIGFILE')
        BMAPPERURL = config.get('internal', 'BMAPPERURL')
        # SOLRSERVER = config.get('internal', 'SOLRSERVER')
        # SOLRCORE = config.get('internal', 'SOLRCORE')
        LOCALDIR = config.get('internal', 'LOCALDIR')
        SEARCH_QUALIFIERS = config.get('internal', 'SEARCH_QUALIFIERS').split(',')
        SEARCH_QUALIFIERS = [unicode(x) for x in SEARCH_QUALIFIERS]
        FIELDDEFINITIONS = config.get('internal', 'FIELDDEFINITIONS')
        CSVPREFIX = config.get('internal', 'CSVPREFIX')
        CSVEXTENSION = config.get('internal', 'CSVEXTENSION')
        # TITLE = config.get('internal', 'TITLE')
        SUGGESTIONS = config.get('internal', 'SUGGESTIONS')
        LAYOUT = config.get('internal', 'LAYOUT')

        try:
            VERSION = popen("cd " + settings.BASE_PARENT_DIR + " ; /usr/bin/git describe --always").read().strip()
            if VERSION == '':  # try alternate location for git (this is the usual Mac location)
                VERSION = popen("/usr/local/bin/git describe --always").read().strip()
        except:
            VERSION = 'Unknown'

    except:
        raise
        print 'error in configuration file %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + configFileName)
        print 'this webapp will probably not work.'

    return MAXMARKERS, MAXRESULTS, MAXLONGRESULTS, MAXFACETS, IMAGESERVER, BMAPPERSERVER, BMAPPERDIR, BMAPPERURL, BMAPPERCONFIGFILE, CSVPREFIX, CSVEXTENSION, LOCALDIR, SEARCH_QUALIFIERS, EMAILABLEURL, SUGGESTIONS, LAYOUT, CSPACESERVER, INSTITUTION, VERSION, FIELDDEFINITIONS, DERIVATIVECOMPACT, DERIVATIVEGRID, SIZECOMPACT, SIZEGRID

# read this app's config file
MAXMARKERS, MAXRESULTS, MAXLONGRESULTS, MAXFACETS, IMAGESERVER, BMAPPERSERVER, BMAPPERDIR, BMAPPERURL, BMAPPERCONFIGFILE, CSVPREFIX, CSVEXTENSION, LOCALDIR, SEARCH_QUALIFIERS, EMAILABLEURL, SUGGESTIONS, LAYOUT, CSPACESERVER, INSTITUTION, VERSION, FIELDDEFINITIONS, DERIVATIVECOMPACT, DERIVATIVEGRID, SIZECOMPACT, SIZEGRID = loadConfiguration('internal')
print 'Configuration successfully read'


def loadFields(fieldFile):
    # get "frontend" configuration from the ... frontend configuration file
    print 'Reading field definitions from %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + fieldFile)

    LOCATION = ''
    DROPDOWNS = []
    FACETS = {}

    FIELDS, PARMS, SEARCHCOLUMNS, SEARCHROWS, SOLRSERVER, SOLRCORE, TITLE, DEFAULTSORTKEY = getParms(
        path.join(settings.BASE_PARENT_DIR, 'config/' + fieldFile))

    for p in PARMS:
        if 'dropdown' in PARMS[p][1]:
            DROPDOWNS.append(PARMS[p][4])
        if 'location' in PARMS[p][1]:
            LOCATION = PARMS[p][3]

    if LOCATION == '':
        print "LOCATION not set, please specify a variable as 'location'"

    facetfields = [f['solrfield'] for f in FIELDS['Search'] if f['fieldtype'] == 'dropdown']

    # facetNames = [f['name'] for f in FIELDS['Facet']]
    #facetfields = []

    #for f in FIELDS['Search']:
    #    if 'dropdown' in f['fieldtype'] and not f['name'] in facetNames:
    #        facetfields.append(f['solrfield'])

    # create a connection to a solr server
    s = solr.SolrConnection(url='%s/%s' % (SOLRSERVER, SOLRCORE))

    try:
        response = s.query('*:*', facet='true', facet_field=facetfields, fq={},
                           rows=0, facet_limit=1000, facet_mincount=1, start=0)

        print 'Solr search succeeded, %s results' % (response.numFound)

        # facets = getfacets(response)

        facets = response.facet_counts
        facets = facets['facet_fields']
        _facets = {}
        for key, values in facets.items():
            _v = []
            for k, v in values.items():
                _v.append((k, v))
            _facets[key] = sorted(_v, key=lambda (a, b): b, reverse=True)
        facets = _facets

        for facet, values in facets.items():
            print 'facet', facet, len(values)
            FACETS[facet] = sorted(values, key=lambda tup: tup[0])
            # build dropdowns for searching
            for f in FIELDS['Search']:
                #if f['solrfield'] == facet and 'dropdown' in f['fieldtype']:
                if 'dropdown' in f['fieldtype'] and f['solrfield'] == facet:
                    # tricky: note we are in fact inserting the list of dropdown
                    # values into the existing global variable FIELDS
                    f['dropdowns'] = sorted(values, key=lambda tup: tup[0])

    #except:
    except Exception as inst:
        #raise
        errormsg = 'Solr query for facets failed: %s' % str(inst)
        solrIsUp = False
        print 'Solr facet search failed. Concluding that Solr is down or unreachable... Will not be trying again! Please fix and restart!'

    # figure out which solr fields are the required ones...
    REQUIRED = []
    requiredfields = 'csid mainentry location accession objectno sortkey blob'.split(' ')
    for p in PARMS:
        for r in requiredfields:
            if r in PARMS[p][1]:
                if PARMS[p][3] not in REQUIRED:
                    REQUIRED.append(PARMS[p][3])

    return DROPDOWNS, FIELDS, FACETS, LOCATION, PARMS, SEARCHCOLUMNS, SEARCHROWS, SOLRSERVER, SOLRCORE, TITLE, DEFAULTSORTKEY, REQUIRED

# on startup, do a query to get options values for forms...
DROPDOWNS, FIELDS, FACETS, LOCATION, PARMS, SEARCHCOLUMNS, SEARCHROWS, SOLRSERVER, SOLRCORE, TITLE, DEFAULTSORTKEY, REQUIRED = loadFields(FIELDDEFINITIONS)
print 'Reading field definitions from %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + FIELDDEFINITIONS)
