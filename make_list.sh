#!/bin/bash
#History:
#   Michael	Nov,03,2016
#Program:
#

DEBUG="False"

if [[ $DEBUG == "True" ]];then
    SUMMARY=/dev/stdout
    README=/dev/stderr
else
    SUMMARY="./SUMMARY.md"
    README="README.md"
fi

dirs=$(find -maxdepth 1 -type d -not -path "./.*" | egrep -v '^\.$')

function make_readme() {
    if [[ ! -d ${1} ]];then
        return 127
    fi
    cd ${1}
    echo -e "# ${1:2}\n\n" > ${README}
    for file in $(find . -name '*.md' | egrep -v 'README\.md')
    do
        filename=$(basename -s .md ${file})
        echo "* [${filename}](${file})" >> ${README}
    done
    cd ..
}

echo -e "# Summary\n\n* [Introduction](${README})" > ${SUMMARY}

for dir in ${dirs}
do
    make_readme ${dir}
    echo "* [${dir:2}](${dir}/README.md)" >> ${SUMMARY}
    for file in $(find ${dir} -name '*.md' | egrep -v '(.*ipynb|README\.md)')
    do
        filename=$(basename -s .md ${file})
        echo "    * [${filename}](${file})" >> ${SUMMARY}
    done
done
