## Atomic-Caldera
A Python 3 script to convert Red Canary Atomic Red Team Tests to MITRE Caldera Stockpile YAML ability files.

# Backstory
While looking into tools to help test and develop Red/Blue (Purple) at my employer, I investigated MITRE's Caldera (https://github.com/mitre/caldera) and liked what I saw but, the number of included tests was small. I also looked at Red Canay's Atomic Red Team (https://github.com/redcanaryco/atomic-red-team), there were a lot of tests but I didn't like the idea of deploying and using scripts locally on endpoints for testing. I very much liked Sandcat (https://github.com/mitre/sandcat), I could easily run it from endpoints and perform tests from a central Caldera server.

I looked around and did not find any tools to convert Red Canary's Atomic Red Team tests to MITRE Caldera Stockpile (https://github.com/mitre/stockpile) format. My desire to quickly build a library using the high quality tests provided by Red Canary in MITRE's Caldera framework drove me to write a "quick" script.

# Requirements
Python 3.6.8+ with the following libraries installed
* PyYAML - https://pyyaml.org/wiki/PyYAML
* STIX2 - https://github.com/oasis-open/cti-python-stix2

Atomic-Caldera requires the following repositories be stored locally somewhere:
* https://github.com/redcanaryco/atomic-red-team
* https://github.com/mitre/cti

# Installation
Install required Python modules:
```
pip install -r requirements.txt
```
Clone the Red Canary Atomic Red Team repository:
```
git clone https://github.com/redcanaryco/atomic-red-team.git
```
Clone the MITRE CTI repository:
```
git clone https://github.com/mitre/cti.git
```
# Usage
Atomic-Caldera requires only two parameters to run. The input directory where the Red Canary Atomic Red Team "atomics" folder is located and the path to the MITRE CTI repository. The output folder option and CSV file options are optional, if they are not supplied, Atomic-Caldera will save these files in the current working directory.
```
usage: Atomic-Caldera.py [-h] [-i INPUTDIR] [-a ATTRIBUTEDIR] [-c CTI]
                         [-o CSV]

Convert Red Canary Attomic Red Team YAML files to Caldera Stockpile YAML
files.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTDIR, --inputdir INPUTDIR
                        The Red Canary "atomics" folder path.
  -a ATTRIBUTEDIR, --attributedir ATTRIBUTEDIR
                        The directory that the converted YAML files will be
                        stored in.
  -c CTI, --cti CTI     The path to the MITRE CTI database, ./cti is used by
                        default.
  -o CSV, --csv CSV     The path to the CSV catalog file.
```

*Example*
```
./Atomic-Caldera.py -i ~/repos/atomic-red-team/atomics -c ~/repos/cti
```
*Example*
```
./Atomic-Caldera.py -i ~/repos/atomic-red-team/atomics -c ~/repos/cti -f ~/woring/ -o ~/working/atomic-caldera.csv
```
# License
See the [LICENSE](https://github.com/xenoscr/Atomic-Caldera/blob/master/LICENSE)

# Credits
CTI and Caldara are maintained by MITRE: @mitre - https://github.com/mitre
Atomic Red Team is maintained by Red Canary Co.: @redcanaryco - https://github.com/redcanaryco
