#!/bin/bash
percent=$(coverage report -m | tail -1 | grep -o '....$' | sed -E 's/[^0-9]+//g')
if [[ $percent -eq 100 ]]
then
    color="brightgreen"
elif [[ $percent -gt 80 ]]
then
    color="green"
elif [[ $percent -gt 60 ]]
then
    color="yellowgreen"
elif [[ $percent -gt 40 ]]
then
    color="yellow"
elif [[ $percent -gt 20 ]]
then
    color="orange"
else
    color="red"
fi
#sed 's/[0-9]\+%25-[a-z]\+/{$percent}%25-green/g' README.md
sed -E -i '' "s/[0-9]+%25-[a-z]+/${percent}%25-${color}/" README.md
