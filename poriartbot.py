#!/usr/bin/python

"""
Overall functionality:
The bot reads spreadsheet data regarding public art at the city of Pori, Finland
and updates Wikidata items based on the spreadsheet data and
also based on some general facts such as all the pieces of art reside in Finland.
The spreadsheet has been created and is upkept by the Pori Art Museum
(http://www.poriartmuseum.fi/).

The functionality in a bit more detail:
1. The spreadheet is read by using the requests library. 
2. The spreadsheet is read line by line utilizing the csv.reader
2.1. If the first column of the spreadsheet row contains a link to an existing Wikidata item then
2.1.1 Check if the second and third column of the spreadheet row contain coordinates and the Wikidata item does not have coordinate location. Insert coordinates for the item accordingly.
2.1.2 Check if the country claim exists and if not then insert the claim.
2.1.3. Check if the eight column of the spreadsheet row contains Wikipedia link and if the item has the link to Finnish Wikipedia. Insert link accordingly.
2.1.4. Check if the fourth column of the spreadsheet row contains label and if item has Finish label. Insert Finnish label accordingly.
2.1.5. Check if the item has creator claim and if the fifth column of the spredsheet row contains creator name. If the item does not have a creator claim and the column has a creator name then try to find Wikidata item for the creator. Insert the creator claim accordingly.
"""

import pywikibot
import io
import csv
import requests
from urllib import parse
import time
import re
from pywikibot.pagegenerators import WikibaseSearchItemPageGenerator


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def addItemClaim(item, property_id, item_id):
    claim = pywikibot.Claim(repo, property_id)
    target = pywikibot.ItemPage(repo, item_id)
    claim.setTarget(target)
    item.addClaim(claim)


# Real spreadsheet for the Pori public art
sheet_url = "https://docs.google.com/spreadsheets/d/1XYeO5BNS71y2XjLfCHwDExDewKInDOCbqFW6-1gVIBU/pub?output=csv"
#Test sheet
#sheet_url = "https://docs.google.com/spreadsheets/d/1Qq-FF4yO-UopXifnhG8yAyOmmKTs9Bn31pEDJ0Rr-3k/pub?output=csv"

site = pywikibot.Site("wikidata", "wikidata") # The real Wikidata site
#site = pywikibot.Site("test", "wikidata") # Site for testing code
repo = site.data_repository()

coord_location_property = u'P625' # www.wikidata.org
#coord_location_property = u'P125' # test.wikidata.org
instance_of_property = u'P31'
#instance_of_property = u'P82'
publication_date_property = u'P577'
#publication_date_property = u'P151'
creator_property = u'P170'
#creator_property = u'P728'
country_property = u'P17'
#country_property = u'P17'
public_art_item = u'Q557141'
#public_art_item = u'Q2225'
sculpture_item = u'Q860861'
#sculpture_item = u'Q2226'
Finland_item = u'Q33'
#Finland_item = u'Q1672'

r = requests.get(sheet_url) # Get the spreadsheet
r.encoding = 'utf-8'
#pywikibot.output(r.encoding)
#pywikibot.output((r.text)
reader = csv.reader(io.StringIO(r.text)) # The csv.reader expects input stream

next(reader, None) # Skip the header row

for row in reader: # Go through spreadsheet rows
    #pywikibot.output(row)
        
    parsed_url = parse.urlparse(row[0])
    #pywikibot.output(parsed_url)
    if parsed_url.scheme != '':
        item_id = parsed_url.path.split('/')[2]
        pywikibot.output(item_id)
        item = pywikibot.ItemPage(repo, item_id)
        if item.isRedirectPage():
            item = item.getRedirectTarget()
        if item.exists():
            #pywikibot.output(item.title)
            #pywikibot.output(item.claims)

            # If sheet includes coordinates for the piece of art and if the wikidata item does not,
            # then add coordinates for the wikidata item
            if is_float(row[1]) and is_float(row[2]):
                lat = float(row[2])
                lng = float(row[1])

                if not coord_location_property in item.claims:
                    claim = pywikibot.Claim(repo, coord_location_property)
                    target = pywikibot.Coordinate(lat, lng, precision=0.0001)
                    claim.setTarget(target)
                    try:
                        item.addClaim(claim)
                    except CoordinateGlobeUnknownException as e:
                        pywikibot.output(u'Skipping unsupported globe: %s' % e.args)
                
            # Add claims instance of public art and instance of sculpture if the item does not have them
            #if not instance_of_property in item.claims:
            #    pywikibot.output(u'adding instance of public art and sculpture claims')
            #    addItemClaim(item, instance_of_property, public_art_item)
            #    addItemClaim(item, instance_of_property, sculpture_item)
            #else:
                # Check if instance_of_property has targets public art or sculpture
                # and if not then add
            #    found_public_art = False
            #    found_sculpture = False
            #    for claim in item.claims[instance_of_property]:
            #        #pywikibot.output(claim.getTarget().title())
            #        if claim.getTarget().title() == public_art_item:
            #            found_public_art = True
            #        elif claim.getTarget().title() == sculpture_item:
            #            found_sculpture = True

            #    if not found_public_art:
            #        pywikibot.output(u'adding instance of public art claim')
            #        addItemClaim(item, instance_of_property, public_art_item)
            #    if not found_sculpture:
            #        pywikibot.output(u'adding instance of sculpture claim')
            #        addItemClaim(item, instance_of_property, sculpture_item)

            if not country_property in item.claims: # Add country?
                pywikibot.output(u'adding country claim')
                addItemClaim(item, country_property, Finland_item)
                
            #if not publication_date_property in item.claims: # Add publication date?
            #    claim = pywikibot.Claim(repo, publication_date_property)
            #    try: # Try to parse date in format 11/23/1990
            #        pub_time = time.strptime(row[5], "%m/%d/%Y")
            #        pywikibot.output(u'adding publication date claim')
            #        pywikibot.output("" + str(pub_time.tm_mday) + "." + str(pub_time.tm_mon) + "." + str(pub_time.tm_year))
            #        target = pywikibot.WbTime(year=pub_time.tm_year, month=pub_time.tm_mon, day=pub_time.tm_mday)
            #        claim.setTarget(target)
            #        item.addClaim(claim)
            #    except ValueError:
            #        try: # Try to parse date in format 23.11.1990
            #            pub_time = time.strptime(row[5], "%d.%m.%Y")
            #            pywikibot.output(u'adding publication date claim')
            #            pywikibot.output("" + str(pub_time.tm_mday) + "." + str(pub_time.tm_mon) + "." + str(pub_time.tm_year))
            #            target = pywikibot.WbTime(year=pub_time.tm_year, month=pub_time.tm_mon, day=pub_time.tm_mday)
            #            claim.setTarget(target)
            #            item.addClaim(claim)
            #        except ValueError:
                        # If could not create date via strptime, try to find four digits and assume them to be the publication year
            #            m = re.search('\d{4}', row[5])
            #            if m != None:
            #                pywikibot.output(u'adding publication date claim')
            #                pywikibot.output(m.group(0))
            #                target = pywikibot.WbTime(year=m.group(0))
            #                claim.setTarget(target)
            #                item.addClaim(claim)
                
            if row[7] != '': # The piece of art has a Finnish Wikipedia page?
                #pywikibot.output(item.sitelinks)
                if u'fiwiki' not in item.sitelinks:
                    pywikibot.output(u'adding Wikipedia link')
                    parts = row[7].split('/')
                    page_title = parts[len(parts)-1].replace("_", " ")
                    page_title = parse.unquote(page_title)
                    #pywikibot.output(page_title)
                    item.setSitelink(sitelink={'site': 'fiwiki', 'title': page_title}, summary=u'Set sitelink')
                        
            if row[3] != '': # Add Finish label if the wikidata item does not have it
                #pywikibot.output(item.labels)
                if u'fi' not in item.labels:
                    pywikibot.output(u'adding Finish label')
                    item.editLabels(labels={'fi': row[3]}, summary=u'Add Finnish label')
                
            if creator_property not in item.claims and row[4] != '': # Add creator claim if the item does not have it and wikidata item of the creator is found via the page generator
                gen = WikibaseSearchItemPageGenerator(row[4], language="fi", site=site)
                if gen:
                    items = list(enumerate(gen))
                    if len(items) == 1:
                        pywikibot.output(u'adding creator claim')
                        item_id = items[0][1].title()
                        addItemClaim(item, creator_property, item_id)
