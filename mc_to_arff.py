#!/usr/bin/python

import json
import pprint
import sys

PP = pprint.PrettyPrinter(indent=4)

input_file = open(sys.argv[1], "r")
game_list = json.loads(input_file.read())
input_file.close()

output_file = open(sys.argv[2], "w")
output_file.write("%% Using data from: %s\n" % input_file.name)
output_file.write('@relation "mc_scores"\n\n')

# run through data to generate attributes list
attributes_list = set()
for game in game_list:
    for key, val in game.items():
        if not (key in ["gb_title", "mc_score", "mc_title", "platform"]):
            attributes_list.add(key)

attributes_list = list(attributes_list)
attributes_list.sort()

output_file.write('@attribute "mc_title" string\n')
output_file.write('@attribute "platform" string\n')
for attribute in attributes_list:
    output_file.write('@attribute "%s" real\n' % attribute.replace(" ", "_"))
output_file.write('@attribute "mc_score" real\n\n')



# do a second pass to write out each row
output_file.write("@data\n")
for game in game_list:
    mc_title = game["mc_title"]
    platform = game["platform"]

    output_file.write('"%s","%s",' % (mc_title, platform))
    for attribute in attributes_list:
        score = None
        if attribute in game:
            score = str(game[attribute])
        else:
            score = "?"
        output_file.write("%s," % score)

    mc_score = game["mc_score"]
    output_file.write("%s\n" % mc_score)



output_file.close()
