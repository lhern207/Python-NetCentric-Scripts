#!/usr/local/bin/python
#A program that given two user provided lists, finds their intersection

input1 = raw_input("Enter a list of items separated by a space: ")
list1 = input1.split(' ')
input2 = raw_input("Enter a second list of items separated by a space: ")
list2 = input2.split(' ')
commonlist = []

for item in list1:
    if item in list2:
       commonlist.append(item)

if commonlist == []:
    print "The lists do not intersect. They do not have items in common"
else:
    print "The intersection of the two lists is the following list: ", commonlist
