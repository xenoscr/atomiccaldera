# Atomic-Caldera
A Python 3 script to convert Red Canary Atomic Red Team Tests to MITRE Caldera Stockpile YAML ability files.

## Backstory
While looking into tools to help test and develop Red/Blue (Purple) teams by running MITRE ATT&CK mapped tests, I investigated MITRE's Caldera (https://github.com/mitre/caldera) and liked what I saw. I did not like that Caldera does not included many abilties/tests by default. I also looked at Red Canay's Atomic Red Team (https://github.com/redcanaryco/atomic-red-team), there are lot of tests included with Atomic Red Team but the included testing framework wasn't as nice as Caldera. I also like the Sandcat (https://github.com/mitre/sandcat) plugin included with Caldera. It can easily be run on many different endpoints, it is light weight, and provides the capability to perform tests from a central Caldera server. By combining the tests from Red Canary's Atomic Red Team with the testing framework of MITRE's Caldera the best of both tool sets could be enjoyed.

I looked around and did not find any tools to convert Red Canary's Atomic Red Team tests to MITRE Caldera Stockpile (https://github.com/mitre/stockpile) format. My desire to quickly build a library using the high quality tests provided by Red Canary in MITRE's Caldera framework drove me to write a "quick" script. This desire led me down a path of developing the tool as a plugin to MITRE's Caldera. This most recent update can now be used with Caldera as a plugin.

## Requirements
Python 3.6.8+ with the following libraries installed
* PyYAML - https://pyyaml.org/wiki/PyYAML
* STIX2 - https://github.com/oasis-open/cti-python-stix2

Atomic-Caldera requires the following repositories be stored locally somewhere:
* https://github.com/redcanaryco/atomic-red-team
* https://github.com/mitre/cti

## Installation
Clone the repository to MITRE's Caldera "plugins" folder:
```
cd <path to caldera/plugins>
git clone https://github.com/xenoscr/Atomic-Caldera.git
```
Rename the folder (will change, eventually.):
```
mv Atomic-Caldera atomiccalera
```
Change directories:
```
cd atomiccaldera
```
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
Edit the conf/artconf.yml file to update the paths to point to your Atomic Red Team and CTI repositories.
Edit Caldera's local.yml file and add atomiccaldera to the plugins section.

## Usage
### Atomic-Caldera
The first time you access the Atomic Caldera plugin you will need to import the Atomic Red Team YAML files to populate Atomic Caldera's database. To do this click the "Add Abilities" button. Adding the abilities for the first time will take some time to complete, please be patient, the status will update when the import is completed.
![Click "Add Abilities"](images/addabilites.png?raw=true "Add Abilities")
#### Selecting an Ability
To select an ability:
1. First select a tactic "Select ATT&CK tactic" drop down.
2. Next select the ability from the "Select ability" drop down.
   ![Selecting an ability](images/selectability.png?raw=true "Select Ability")

   After you have selected an ability you can use the left and right arrows to quicly move through the list of available abilities related to the selected tactic.
#### Saving an Ability
If you have made changes to an ability and wish to save them:
1. Click the "Save Ability" button.
   ![Save Ability](images/saveability.png?raw=true "Save Ability")
#### Saving Variables
If you have made changes to variables and wish to save them:
1. Click the "Save Variables" button.  
   ![Save variables](images/savevariables.png?raw=true "Save Variables")
#### Export a Single Ability
If you wish to export the selected ability only to Stockpile:
1. Click the Export Ability button.  
   ![Export ability](images/exportone.png?raw=true "Export single ability")&nbsp;
#### Export All Abilites
If you wish to export all of the abilities from Atomic Caldera to Stockpile:
1. Click the Export All Abilities button.  
   ![Export All Abilities](images/exportall.png?raw=true "Export All Abilities")
#### Reloading Data (i.e. Start over)
If you wish to delete everything that has been imported and wish to start over, do so by:
1. Click the Reload Abilities button.  
   ![Reload Abilities](images/reloadabilities.png?raw=true "Reload Abilities")
2. Click the Yes button.  
   ![Yes](images/yes.png?raw=true "Yes")
   After clicking yes, it will then take some time for the abilites to complete reloading.
NOTE: It is necessary to restart Caldera to view the new abilties. At the moment there is no way to force Chain to relaod its database from the GUI.
## To-Do
Stil not perfect but, it gets the bulk fo the work done at this time. I would like to work on/fix the following eventually:
- [ ] Include the ability to build adversaries from ART tests. Chain removed the ability to edit adversaries via the GUI which makes it more difficult to quickly build adversaries.
## ChangeLog
### v3.0
What didn't change?
* Atomic Caldera is now a plugin for MITRE's Caldera
* Added ability to edit and save changes to abilites and variables
* Added ability to export ablilites directly to Stockpile YAML files.
### v2.0
* Changed the default output to generate Caldera YML files with the variables intact. i.e. #{variable}
* Added a second CSV file output to output the CSV values so they can be edited before being imported to customize the tests.
* Added the Update-AtomicVariables.py script to populate the variable values and save the completed tests to a new directory.
* Added a wrapper script to support running Command Prompt commands using Caldera. Caldara supports Bash and PowerShell commands only. Some of the Atomic Red Team tests that were meant to run under the Command Prompt did not work properly due to formatting issues. The wrapper script spawns a new Command Prompt window and sends the keystrokes to run the commands. Once complete it copies the Command Prompt stdout to the clipboard so that the results can be displayed in Caldera's results window.
## License
See the [LICENSE](https://github.com/xenoscr/Atomic-Caldera/blob/master/LICENSE)

## Credits
* CTI and Caldara are maintained by MITRE: @mitre - https://github.com/mitre
* Atomic Red Team is maintained by Red Canary Co.: @redcanaryco - https://github.com/redcanaryco
