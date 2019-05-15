#!/usr/bin/python3

###############################################################################
# Name: Atomic-Caldera.py
# Author: Conor Richard (@xenosCR)
#
# Description: This script was written to convert the YAML files in 
# Red Canarie's Atomic Red Team libary to a format to the YAML format that 
# MITRE's Caldera Stockpile plugin can consume nativly.
#
# This script will loop through all atomic tests in the provided path and
# extract each test, assign it a UID and save it to a new YAML file in a 
# categorized abiltiy folder. It will also generate a CSV file to catalog
# the converted techniques.
#
# The CSV catalog file serves two purposes:
# 1. A helpful list to aid in the building of Calera Adversaries/test.
# 2. The CSV file is checked to ensure that tests are not duplicated by
#    checking the MITRE ATT&CK ID and Command combination.
#
# Known Issue(s):
# 1. Some tests from Red Canay's Atomic Red Team are very manual. Due to this,
#    those tests are not converted automatically by this script. This script
#    provides best effort to automatically convert the majority of tests.
# 2. Some of the manual tests still slip by, you will need to spot check
#    converted files before relying on them for testing. Sorry.
#
# Requirements:
# 1. Must have a local copy of Red Canary Atomic Red Team.
# 2. Must have a local copy of MITRE's CTI databse.
# 3. The following python libraries are required:
#    a. yaml
#    b. stix2
#
# Credits:
# Red Canary's Atomic Red Team - https://github.com/redcanaryco/atomic-red-team
# MITRE's Caldera - https://github.com/mitre/caldera
###############################################################################

import argparse, collections, csv, logging, os, sys, re, uuid, yaml
from stix2 import FileSystemSource
from stix2 import Filter

class cmdStr(str):
    pass

def cmd_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

def getMITREPhase(fs, attackID):
    filter = [
            Filter('type', '=', 'attack-pattern'),
            Filter('external_references.external_id', '=', attackID)
        ]
    result = fs.query(filter)
    if result:
        return result[0].kill_chain_phases[0].phase_name
    else:
        return None

# Taken from https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
# to save time
def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def main(inputDir, ouptutDir, csvPath, ctiPath):
    logging.debug('Starting main function.')
    # Load the MITRE library
    fs = FileSystemSource(os.path.join(ctiPath, 'enterprise-attack/'))

    # Check for an existing CSV file
    try:
        csvFile = []
        with open(csvPath, 'r') as oldCSVFile:
            reader = csv.DictReader(oldCSVFile)
            for line in reader:
                csvFile.append(line)

        logging.debug('Successfully loaded CSV file.')
    except:
        csvFile = []
        logging.debug('CSV was not loaded, creating empty list.')

    # Walk the directory provided as the input directory to find
    # the YAML files to process.
    # ----------------------------------------------------------
    for root, dirs, files in os.walk(inputDir):
        for procFile in files:
            fullFile = os.path.join(root, procFile)
            if os.path.splitext(fullFile)[-1].lower() == '.yaml':
                print("Processing: {}".format(fullFile))
                # Load the YAML file
                with open(fullFile, 'r') as yamlFile:
                    try:
                        yamlData = yaml.load(yamlFile, Loader=yaml.Loader)
                        logging.debug('Successfully loaded: {}.'.format(fullFile))
                    except:
                        logging.debug('Unable to load: {}.'.format(fullFile))
                        raise SystemExit('Unable to load: {}.'.format(fullFile))

                # Get the description
                if 'display_name' in yamlData.keys():
                    displayName = yamlData['display_name']
                    #print(displayName)

                # Get the attackID & Kill Phase
                if 'attack_technique' in yamlData.keys():
                    attackID = yamlData['attack_technique']
                    tactic = getMITREPhase(fs, attackID)
                    #print(attackID)
                    #print(tactic)
                    if tactic == None:
                        tactic = 'unknown'
                else:
                    logging.debug('No attack in this YAML, continuing.')
                    continue

                # Get the testDescription, name, command, and executor
                if 'atomic_tests' in yamlData.keys():
                    # Loop through each Atomic test (Atomic Red Team lists multiple tests per YAML file)
                    for atomic in yamlData['atomic_tests']:
                        # Grab the attack name
                        attackName = atomic['name']
                        # Grab the attack description
                        testDescription = atomic['description']
                        # Some tests do not have a 'command' key, skip it if it does not.
                        if 'command' in atomic['executor'].keys():
                            # grab the command
                            command = atomic['executor']['command']
                            # If input arguments exist, replace them by looping through each
                            # and using regex replacement.
                            if 'input_arguments' in atomic.keys():
                                for argument in atomic['input_arguments'].keys():
                                    try:
                                        command = re.sub(r"\#{{{argName}}}".format(argName = str(argument)), str(atomic['input_arguments'][argument]['default']).encode('unicode-escape').decode(), command)
                                    except:
                                        logging.error('Unable to encode command.')
                                        raise SystemExit

                            # Grab the executor name
                            executor = atomic['executor']['name']
                        else:
                            command = ''
                            executor = ''

                        if (executor.lower() == 'sh' or executor.lower() == 'bash'):
                            executor = 'bash'
                        elif (executor.lower() == 'command_prompt' or executor.lower() == 'powershell'): 
                            executor = 'psh'

                        logging.debug('Collected attack name: {}'.format(attackName))
                        logging.debug('Collected attack executor: {}'.format(executor))
                        logging.debug('Collected attack command: {}'.format(command))

                        # Check to see if the command has been catalogued in the CSV previously
                        if not any((line['attackID'] == attackID) and (line['command'] == command) for line in csvFile):
                            logging.debug('Collecting new YAML info.')

                            # Ensure we don't somehow use a duplicate UUID value
                            uuidBool = True

                            while(uuidBool):
                                attackUUID = uuid.uuid4()
                                if not any(line['attackUUID'] == str(attackUUID) for line in csvFile):
                                        uuidBool = False

                            # Put the custom dictionary together that will be exported/dumped to a YAML file
                            # the 'command' is formatted as a scalar string.
                            newYAML = [{ 'id': str(attackUUID),
                                'name': displayName,
                                'description': '{} (Atomic Red Team)'.format(testDescription.strip().replace('\n', ' ').replace('  ', ' ')),
                                'tactic': tactic,
                                'technique': { 'attack_id': attackID, 'name': attackName },
                                'executors': { executor: { 'command': cmdStr(command) }}}]

                            logging.debug(newYAML)

                            # Generate New YAML

                            # Make sure the abilities directory exists and create it if it does not.
                            try:
                                abilityDir = os.path.join(ouptutDir, 'abilities/')
                                if not os.path.exists(abilityDir):
                                    os.makedirs(abilityDir)
                                    logging.debug('Ability directory created: {}'.format(abilityDir))
                                else:
                                    logging.debug('Ability directory exists: {}'.format(abilityDir))
                            except:
                                logging.error('Failed to create the abilty directory.')
                                raise SystemExit

                            # Make sure the tactic directory exists and create it if it does not.
                            try:
                                if not os.path.exists(os.path.join(abilityDir, tactic)):
                                    os.makedirs(os.path.join(abilityDir, tactic))
                                    logging.debug('Tactic directory created: {}'.format(os.path.join(abilityDir, tactic)))
                                else:
                                    logging.debug('Tactic directory exists: {}'.format(os.path.join(abilityDir, tactic)))
                            except:
                                logging.error('Tactic is empty?')
                                raise SystemExit

                            # Write the YAML file to the correct directory using the UUID as the name.
                            try:
                                with open(os.path.join(abilityDir, tactic, '{}.yml'.format(str(attackUUID))), 'w') as newYAMLFile:
                                    dump = yaml.dump(newYAML, default_style = None, default_flow_style = False, allow_unicode = True, encoding = None, sort_keys = False)
                                    newYAMLFile.write(dump)
                                logging.debug('YAML file written: {}'.format(os.path.join(abilityDir, tactic, '{}.yml'.format(str(attackUUID)))))
                            except Exception as e:
                                logging.error('Error creating YAML file.')
                                print(e)
                                raise SystemExit

                            # Append the newly converted ability information to the variable that will written to the CSV file
                            newLine = { 'attackUUID': attackUUID, 'attackID': attackID, 'command': command }
                            csvFile.append(newLine)
                        else:
                            logging.debug('The technique already exists.')

        # Write the content of CSV file to disk
        with open(csvPath, 'w', newline='') as newCSVFile:
            fieldNames = ['attackUUID', 'attackID', 'command']
            writer = csv.DictWriter(newCSVFile, fieldnames = fieldNames)

            writer.writeheader()
            for line in csvFile:
                writer.writerow(line)

if __name__ == "__main__":
    # String representer foy PyYAML to format the command string
    yaml.add_representer(cmdStr, cmd_presenter)

    # Setup Debugging messages
    logLvl = logging.ERROR
    logging.basicConfig(level=logLvl, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('Debugging logging is on.')

    # Parse the command arguments and display a usage message if incorrect parameters are provided.
    parser = argparse.ArgumentParser(description = 'Convert Red Canary Attomic Red Team YAML files to Caldera Stockpile YAML files.')
    parser.add_argument("-i", "--inputdir", type=str, help='The Red Canary \"atomics\" folder path.')
    parser.add_argument("-f", "--fileoutdir", type=str, help='The directory that the converted YAML files will be stored in.')
    parser.add_argument("-c", "--cti", type=str, help='The path to the MITRE CTI database, ./cti is used by default.')
    parser.add_argument("-o", "--csv", type=str, help='The path to the CSV catalog file.')
    args = parser.parse_args()

    # Get the CSV File location
    if args.csv:
        csvPath = args.csv
    else:
        csvPath = os.path.join(os.getcwd(), 'atomic-caldera.csv')

    if os.path.exists(csvPath):
        try:
            with open(csvPath, 'r') as csvFile:
                line = csvFile.readline()
        except:
            parser.print_help(sys.stderr)
            print('\n\n')
            logging.error('The provided path to the CSV file is invalid or the CSV file is corrupted.')
            raise SystemExit

        if not line == 'attackUUID,attackID,command\n':
            parser.print_help(sys.stderr)
            print('\n\n')
            logging.error('The provided path to the CSV file is invalid or the CSV file is corrupted.')
            raise SystemExit
    else:
        logging.debug('The CSV fle does not exist, it will be created.')

    # Get the MITRE CTI database location from the provided path or default location
    if args.cti:
        ctiPath = args.cti
    else:
        curPath = os.path.dirname(os.path.realpath(__file__))
        ctiPath = os.path.join(curPath, 'cti/')

    if not (os.path.exists(ctiPath) and os.path.exists("{ctiPath}/enterprise-attack/".format(ctiPath = ctiPath))):
        parser.print_help(sys.stderr)
        print('\n\n')
        logging.error('The provided path to the MITRE CTI database is incorrect or corrupt.')
        raise SystemExit

    logging.debug('The provided CTI path is: {}'.format(ctiPath))
    
    # Check the output directory
    if args.fileoutdir:
        if os.path.exists(args.fileoutdir):
            logging.debug('Checking fileoutdir.')
            abilityDir = os.path.join(args.fileoutdir, 'abilities/')
            if os.path.exists(abilityDir):
                logging.debug('Checking for existing YAML files in: {}.'.format(abilityDir))
                fileCount = 0
                for root, dirs, files in os.walk(abilityDir):
                    for procFile in files:
                        fullFile = os.path.join(root, procFile)
                        if os.path.splitext(fullFile)[-1].lower() == '.yml':
                            fileCount += 1
                if fileCount > 0:
                    answer = query_yes_no('The directory already contains YAML files, please be sure you are not going to duplicate files. Would you like to continue?')
                    if answer == True:
                        outputDir = args.fileoutdir
                    else:
                        print('You chose not to coninue. Please double-check your work and try again if needed.')
                        raise SystemExit
                else:
                    outputDir = args.fileoutdir
            else:
                logging.debug('No abilities directory found in provided output path')
                outputDir = args.fileoutdir
        else:
            parser.print_help(sys.stderr)
            print('\n\n')
            logging.debug('The provided output directory is invalid\n')
            raise SystemExit
    else:
        logging.debug('The provided output directory was not provided, using current working directory.\n')
        outputDir = os.getcwd()

    # Get the Red Canary Atomic Red Team repository location
    if args.inputdir:
        if os.path.exists(args.inputdir) and os.path.exists("{argPath}/T1002".format(argPath = args.inputdir)):
            main(args.inputdir, outputDir, csvPath, ctiPath)
        else:
            parser.print_help(sys.stderr)
            print('\n\n')
            logging.error('The provided input directory is not valid or does not exist.\n')
            raise SystemExit
    else:
        parser.print_help(sys.stderr)
        print('\n\n')
        logging.error('No input directory was provided.\n')
        raise SystemExit
