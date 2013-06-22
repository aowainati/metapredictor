#!/usr/bin/python

import json
import pprint
import random
import time
import traceback
import sys

from bs4 import BeautifulSoup
from datetime import datetime
from Levenshtein import distance
from urllib import quote_plus
from urllib2 import urlopen


BASE_SEARCH_URL = "http://www.metacritic.com/search/game/{transformed_title}/results"
BASE_CRITICS_PAGE_URL = "http://www.metacritic.com{game_path}/critic-reviews?num_items=100"
PP = pprint.PrettyPrinter(indent=4)


def isValidGame (game):
    success = ("name" in game)
    success &= (game["name"] != "")
    success &= ("original_release_date" in game)
    success &= (game["original_release_date"] != None)

    return success

def editDistance (string1, string2):
    dist = distance(string1, string2)
    print "Comparing %s and %s, distance: %d" % (string1, string2, dist)
    return dist

def parseCriticsData (mc_title, gb_title, platform, mc_score, critics_url):
    feature_dict = {
        "mc_title" : mc_title,
        "gb_title" : gb_title,
        "platform" : platform,
        "mc_score" : mc_score
        }

    critics_soup = BeautifulSoup(urlopen(critics_url).read())

    reviews = critics_soup.findAll("li", { "class" : "critic_review" })
    for review_soup in reviews:
        critic_name = review_soup.find("div", { "class" : "source" }).find("a").text.strip().encode('utf-8')
        score = int(review_soup.find("div", { "class" : "critscore" }).text.strip())
        feature_dict[critic_name] = score

    return feature_dict




# Parse list of games
# For each game, validate it
# Fire a search query, pull the top result url
# Transform top result URL into critics page URL
# Fire a critics page query, generate critic-to-score hash


input_platform = sys.argv[1]
input_file = open("/Users/aowainati/Documents/code/giantbomb/data/"+input_platform+".json", "r")
game_list = json.loads(input_file.read())
input_file.close()

training_data = []
success_count = 0
error_count = 0

for game in game_list:
    if isValidGame(game):
        gb_title = game["name"].encode('utf-8')
        release_date = game["original_release_date"]

        print "------------"
        print "Checking game: " + gb_title
        search_url = BASE_SEARCH_URL.format(transformed_title=quote_plus(gb_title.replace(":", "").replace("-", " ").replace("_", " ")))
        print "Search URL: " + search_url

        try:
            search_soup = BeautifulSoup(urlopen(search_url).read())
            search_results = search_soup.findAll("li", { "class" : "result" })
            for result_soup in search_results:

                platform = result_soup.find("span", { "class" : "platform" }).text.strip().encode('utf-8')
                link_soup = result_soup.find("a")
                mc_title = link_soup.text.encode('utf-8')
                title_edit_distance = editDistance(gb_title, mc_title)

                if title_edit_distance <= 3 and platform == input_platform:
                    game_path = link_soup["href"]
                    critics_url = BASE_CRITICS_PAGE_URL.format(game_path=game_path)

                    mc_score = int(result_soup.find("span", { "class" : "metascore" }).text.strip())

                    print "Platform: " + str(platform)
                    print "GB Title: " + str(gb_title)
                    print "MC Title: " + str(mc_title)
                    print "Edit Distance: " + str(title_edit_distance)
                    print "Critics URL: " + str(critics_url)
                    print "Feature Hash: "
                    feature_data = parseCriticsData(mc_title, gb_title, platform, mc_score, critics_url)
                    PP.pprint(feature_data)
                    training_data.append(feature_data)
                    success_count += 1

                    break
                else:
                    print "Wrong item"

                sys.stderr.flush()
                sys.stdout.flush()

        except Exception as e:
            error_count += 1
            print traceback.format_exc()

        print "------------"

        time.sleep(3 + random.random())

print "Found data for %d games." % (success_count)
print "Encountered %d errors." % (error_count)
print "Done!"

output_file = open("/Users/aowainati/Documents/code/metacritic/data/"+input_platform+".json", "w")
output_file.write(json.dumps(training_data))
output_file.close()
