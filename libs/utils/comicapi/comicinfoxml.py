# -*- coding: utf-8 -*-

'''
Copyright 2012-2014  Anthony Beville
Copyright 2017 Brian Pepple
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import xml.etree.ElementTree as ET

from .genericmetadata import GenericMetadata


class ComicInfoXML(object):

    def metadataFromString(self, s):
        tree = ET.ElementTree(ET.fromstring(s))

        return self.convertXMLToMetadata(tree)

    def convertXMLToMetadata(self, tree):

        root = tree.getroot()

        if root.tag != 'ComicInfo':
            raise 1
            return None

        metadata = GenericMetadata()
        md = metadata

        # Helper function
        def xlate(tag):
            node = root.find(tag)
            if node is not None:
                return node.text
            else:
                return None

        md.series = xlate('Series')
        md.title = xlate('Title')
        md.issue = xlate('Number')
        md.issueCount = xlate('Count')
        md.volume = xlate('Volume')
        md.alternateSeries = xlate('AlternateSeries')
        md.alternateNumber = xlate('AlternateNumber')
        md.alternateCount = xlate('AlternateCount')
        md.comments = xlate('Summary')
        md.notes = xlate('Notes')
        md.year = xlate('Year')
        md.month = xlate('Month')
        md.day = xlate('Day')
        md.publisher = xlate('Publisher')
        md.imprint = xlate('Imprint')
        md.genre = xlate('Genre')
        md.webLink = xlate('Web')
        md.language = xlate('LanguageISO')
        md.format = xlate('Format')
        md.manga = xlate('Manga')
        md.characters = xlate('Characters')
        md.teams = xlate('Teams')
        md.locations = xlate('Locations')
        md.pageCount = xlate('PageCount')
        md.scanInfo = xlate('ScanInformation')
        md.storyArc = xlate('StoryArc')
        md.seriesGroup = xlate('SeriesGroup')
        md.maturityRating = xlate('AgeRating')

        tmp = xlate('BlackAndWhite')
        md.blackAndWhite = False
        if tmp is not None and tmp.lower() in ["yes", "true", "1"]:
            md.blackAndWhite = True
        # Now extract the credit info
        for n in root:
            if (n.tag == 'Writer' or
                n.tag == 'Penciller' or
                n.tag == 'Inker' or
                n.tag == 'Colorist' or
                n.tag == 'Letterer' or
                n.tag == 'Editor'
                ):
                if n.text is not None:
                    for name in n.text.split(','):
                        metadata.addCredit(name.strip(), n.tag)

            if n.tag == 'CoverArtist':
                if n.text is not None:
                    for name in n.text.split(','):
                        metadata.addCredit(name.strip(), "Cover")

        # parse page data now
        pages_node = root.find("Pages")
        if pages_node is not None:
            for page in pages_node:
                metadata.pages.append(page.attrib)
                # print page.attrib

        metadata.isEmpty = False

        return metadata
