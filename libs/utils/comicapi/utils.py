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


def listToString(l):
    string = ""
    if l is not None:
        for item in l:
            if len(string) > 0:
                string += ", "
            string += item
    return string


def removearticles(text):
    text = text.lower()
    articles = ['and', 'the', 'a', '&', 'issue']
    newText = ''
    for word in text.split(' '):
        if word not in articles:
            newText += word + ' '

    newText = newText[:-1]

    # now get rid of some other junk
    newText = newText.replace(":", "")
    newText = newText.replace(",", "")
    newText = newText.replace("-", " ")

    # since the CV API changed, searches for series names with periods
    # now explicitly require the period to be in the search key,
    # so the line below is removed (for now)
    #newText = newText.replace(".", "")

    return newText
