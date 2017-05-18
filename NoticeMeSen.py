"""This module creates a list of algorithms that don't have implementations
in a set of sane languages on GitHub."""
import httplib2
import json
import urllib.request
import time
from bs4 import BeautifulSoup, SoupStrainer

LANGUAGES_TO_SEARCH = ["python", "java", "C#", "Go", "Haskell", "javascript"]

def unmangle_algorithm(algorithm_name):
    """
    Converts characters that were not properly parsed to their ASCII equivalents
    """
    return algorithm_name.replace('_', ' ') \
    .replace("%20", " ")                    \
    .replace("%27", "'")                    \
    .replace("%E2", "-")                    \
    .replace("%80", "")                     \
    .replace("%93", "")                     \
    .replace("%C3%A5", "a")

def make_git_search_request(language, algorithm):
    """
    GETs a request to Github's search API
    """
    base_request = "https://api.github.com/search/repositories?"
    formatted_request = base_request + "q=" + algorithm + "+language:" + language

    parsed_response = urllib.request.urlopen(formatted_request).read().decode('utf-8')
    num_results = json.loads(parsed_response)["total_count"]
    return num_results

def get_hits_for_algorithm(algorithm_names):
    """
    Queries the Github search API to see how many hits exist for each algorithm.
    Returns a dict with the mapping of {Algorithm : [Unimplemented Languages]}
    """
    mapping_table = {}
    #TODO: Probably a list comprehension way to do this
    for algorithm in algorithm_names:
        for language in LANGUAGES_TO_SEARCH:
            num_results = make_git_search_request(language, algorithm)
            if  num_results != 0 and num_results != len(LANGUAGES_TO_SEARCH):
                if mapping_table.get(algorithm) is None:
                    mapping_table[algorithm] = [language]
                else:
                    mapping_table[algorithm] = mapping_table[algorithm].append(language)
            time.sleep(6)

    return mapping_table

def get_algorithm_list():
    """
    Returns a list of algorithms from wikipedia
    """
    algorithm_names = []
    http = httplib2.Http()
    status, response = http.request("https://en.wikipedia.org/wiki/List_of_algorithms")

    for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        if link.has_attr('href'):
            if (link['href']).startswith('/wiki/'):
                algorithm_name = link['href'][6:]
                algorithm_names.append(unmangle_algorithm(algorithm_name))

    return algorithm_names

#TODO Add more robust testing
def janky_test():
    """
    Janky test. Note that this could fail if someone decides to implement a fast-clipping
    algorithm in some language other than JS.
    """
    print("Testing basic functionality!")
    test_dict = get_hits_for_algorithm(["Fast-clipping"])
    if test_dict["Fast-clipping"][0] is not 'javascript':
        raise AssertionError()
    print("All tests passed!")


if __name__ == "__main__":
    janky_test()
