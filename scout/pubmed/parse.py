#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
'script.py' is created by 'invaana' for the project 'import-pubmed' on 15 December, 2016.


This script will download the files from https://www.nlm.nih.gov/databases/download/pubmed_medline_documentation.html

Download the files from pubmed baseline
ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/





"""
import xml.etree.cElementTree as etree
import logging, datetime, re
formatter = '%(asctime)s - %(lineno)d - %(name)s - %(levelname)s : %(message)s'
logging.basicConfig(filename="./run.log", level=logging.DEBUG,filemode='w', format=formatter)
logger = logging.getLogger(__name__)




def etree_to_dict(t):
    d = {t.tag : map(etree_to_dict, t.iterchildren())}
    d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    d['text'] = t.text
    return d


def make_dict_from_tree(element_tree):
    """Traverse the given XML element tree to convert it into a dictionary.

    :param element_tree: An XML element tree
    :type element_tree: xml.etree.ElementTree
    :rtype: dict
    """
    def internal_iter(tree, accum):
        """Recursively iterate through the elements of the tree accumulating
        a dictionary result.

        :param tree: The XML element tree
        :type tree: xml.etree.ElementTree
        :param accum: Dictionary into which data is accumulated
        :type accum: dict
        :rtype: dict
        """
        if tree is None:
            return accum

        if tree.getchildren():
            accum[tree.tag] = {}
            for each in tree.getchildren():
                result = internal_iter(each, {})
                if each.tag in accum[tree.tag]:
                    if not isinstance(accum[tree.tag][each.tag], list):
                        accum[tree.tag][each.tag] = [
                            accum[tree.tag][each.tag]
                        ]
                    accum[tree.tag][each.tag].append(result[each.tag])
                else:
                    accum[tree.tag].update(result)
        else:
            accum[tree.tag] = tree.text

        return accum

    return internal_iter(element_tree, {})


def parse_xml_to_dict(f):
    """
    This will read the file in the form of .xml and returns a list of pubmed entry dictionaries

    :param f: filename of in .xml format. Eg: medsamp2016a.xml
    :return:
    """
    xml_file_data = open(f).read()
    tree = etree.fromstring(xml_file_data)
    dict_list_data = []
    for i,d in enumerate(tree):
        data = make_dict_from_tree(d)
        # logger.debug( data['MedlineCitation'])
        title = data['MedlineCitation']['Article']['ArticleTitle'].rstrip('.').lstrip('[').rstrip(']')
        journal_title = data['MedlineCitation']['Article']['Journal']['Title'].lstrip('[').rstrip(']')
        pmid = data['MedlineCitation']['PMID']

        try:
            journal_year = int(data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year'])

        except:
            journal_year = re.split('(\d+)', data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'][
                'MedlineDate'])
        finally:
            journal_year = None

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        try:
            if type(data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month']) == str:
                for i, m in enumerate(months):
                    if data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month'] == m or \
                                    data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'][
                                        'Month'] in m:
                        month = i + 1
            else:
                month = int(data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month'])
        except:
            month = 1

        try:
            date = int(data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Day'])
        except:
            date = 1

        try:
            journal_pubdate = datetime.datetime(
                year=journal_year,
                month=month,
                day=date)
        except:
            journal_pubdate = None

        try:
            abstract = data["MedlineCitation"]["OtherAbstract"]["AbstractText"]  # .lstrip('[').rstrip(']')
        except Exception as e:
            abstract = None
        try:
            journal_type = data['MedlineCitation']['Article']['PublicationTypeList']['PublicationType']
        except:
            journal_type = []

        try:
            journal_keywords = data['MedlineCitation']['KeywordList']['Keyword']
        except:
            journal_keywords = []

        try:

            if type(journal_type) == str:
                journal_type = [journal_type, ]

            if type(journal_keywords) == str:
                journal_keywords = [journal_keywords, ]




            if abstract:
                abstract = abstract

            dict_list_data.append({
                'pmid': pmid,
                'title': title,
                'journal_title': journal_title,
                'abstract': abstract,
                'pub_year': journal_year,
                'pub_date': journal_pubdate,
                'journal_keywords_list': journal_keywords,
                'journal_type_list': journal_type,

            })
        except Exception as e:
            logger.error(e)

            logger.error(journal_type)
            logger.error("-=-=-=-=-=-")



    return dict_list_data







