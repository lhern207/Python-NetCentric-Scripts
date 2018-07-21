#!/usr/local/bin/python
#A program that given a user entered list of exam scores and target percentile
#returns the score that corresponds to the given percentile.

inputscores = raw_input("Enter all exam scores separated by a space: ")
listscores = inputscores.split(' ')
intscores = []

for score in listscores:
    intscores.append(int(score))

intscores.sort()
percentile = raw_input("Enter the percentile to find: ")
intpercentile = int(percentile)

if (intpercentile < 0 or intpercentile > 100):
    print "Percentile out of range"
else:
    rank = (len(intscores) + 1) * (float(intpercentile)/100)
    rankfloor = int(rank//1)
    rankfraction = rank%rankfloor
    result = intscores[rankfloor-1] + (rankfraction * (intscores[rankfloor] - intscores[rankfloor-1]))
    print "The " + str(intpercentile) + " percentile score is: " + str(result)
