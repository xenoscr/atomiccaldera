#!/usr/bin/python3

import argparse, collections, csv, fnmatch, logging, os, shutil, sys, re, uuid, yaml

class cmdStr(str):
	pass

def cmd_presenter(dumper, data):
	return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

def checkAbilities(path):
	if os.path.exists(path):
		logging.debug('Checking for existing abilities files.')
		fileCount = 0
		for root, dirs, files in os.walk(path):
			for procFile in files:
				fullFile = os.path.join(root, procFile)
				if os.path.splitext(fullFile)[-1].lower() == '.yml':
					fileCount += 1
				if fileCount > 0:
					return True
				else:
					return False

def checkCSVFile(csvPath):
	if os.path.exists(csvPath):
		try:
			with open(csvPath, 'r') as csvFile:
				line = csvFile.readline()
		except:
			parser.print_help(sys.stderr)
			print('\n\n')
			logging.error('The provided path to the catalog CSV file is invalid or the CSV file is corrupted.')
			raise SystemExit

		if not line == 'attackUUID,attackID,executor,variable,value\n':
			logging.error('The provided path to the catalog CSV file is invalid or the CSV file is corrupted.')
			return False
		else:
			return True
	else:
		logging.debug('The catalog CSV fle does not exist.')
		return False

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
	valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
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
			sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

def main(inputDir, outputDir, csvPath):
	# Load the CSV file
	try:
		csvFile = []
		uniqueUUID = []
		with open(csvPath, 'r') as csvReadFile:
			reader = csv.DictReader(csvReadFile)
			for line in reader:
				csvFile.append(line)
				# Add the attackUUID value to a list of unique UUIDs
				if line['attackUUID'] not in uniqueUUID:
					uniqueUUID.append(line['attackUUID'])
	except:
		logging.error('Unable to read CSV file.')
		raise SystemExit

	# Create a fully copy of the directory first
	shutil.rmtree(outputDir)
	shutil.copytree(inputDir, outputDir, False)

	# Step through each UUID and update the command strings
	for curUUID in uniqueUUID:
		for root, dirnames, filenames in os.walk(inputDir):
			for filename in fnmatch.filter(filenames, '{}.yml'.format(curUUID)):
				curFile = os.path.join(root, filename)

		# Open and parse the YAML file
		with open(curFile, 'r') as yamlFile:
			try:
				yamlData = yaml.load(yamlFile, Loader=yaml.Loader)
				logging.debug('Successfully loaded: {}.'.format(curFile))
				logging.debug(yamlData)
			except:
				logging.debug('Unable to load: {}.'.format(curFile))
				raise SystemExit('Unable to load: {}.'.format(curFile))

		# Get the command that will be updated
		for key in yamlData[0]['executors']:
			for key1 in yamlData[0]['executors'][key]:
				if key1 == 'command':
					command = yamlData[0]['executors'][key]['command']
					logging.debug('Command value found.')
					logging.debug(command)

					# Update the command by looping through the CSV file and applying the appropriate variables
					for line in csvFile:
						if line['attackUUID'] == curUUID:
							command = re.sub(r"\#{{{argName}}}".format(argName = str(line['variable'])), str(line['value']).encode('unicode-escape').decode(), command)

					yamlData[0]['executors'][key]['command'] = cmdStr(command)
					logging.debug('Updated command in YAML variable.')
				else:
					logging.error('Command value not found, exiting.')
					raise SystemExit

		logging.debug(yamlData)

		# Write the YAML file to the correct directory using the UUID as the name.
		newAbilityDir = os.path.join(outputDir, os.path.split(os.path.dirname(curFile))[1])
		if not os.path.exists(newAbilityDir):
			os.makedirs(newAbilityDir)

		newFile = os.path.join(newAbilityDir, filename)
		try:
			with open(newFile, 'w') as newYAMLFile:
				dump = yaml.dump(yamlData, default_style = None, default_flow_style = False, allow_unicode = True, encoding = None, sort_keys = False)
				newYAMLFile.write(dump)
			logging.debug('YAML file written: {}'.format(newFile))
		except Exception as e:
			logging.error('Error creating YAML file.')
			print(e)
			raise SystemExit

if __name__ == "__main__":
	# String representer for PyYAML to format the command string
	yaml.add_representer(cmdStr, cmd_presenter)

	# Setup Debugging messages
	logLvl = logging.DEBUG
	logging.basicConfig(level=logLvl, format='%(asctime)s - %(levelname)s - %(message)s')
	logging.debug('Debugging logging is on.')

	# Parse the command arguments and display a usage message if incorrect parmeters are provided.
	parser = argparse.ArgumentParser(description = 'Populate the variable values in the abilities folder with those provided in the supplied input CSV file.')
	parser.add_argument("-i", "--inputdir", type=str, help='The path to the \"abilities\" folder that needs to be updated.')
	parser.add_argument("-o", "--outputdir", type=str, help='The path to store the updated \"abilities\" folder. If no argument is provided, an \"abilities-populated\" folder will be created.')
	parser.add_argument("-c", "--csv", type=str, help='The CSV file that will be used to update variable values.')

	args = parser.parse_args()

	# Validate the required arguments
	if args.inputdir:
		# Check for the presense of YAML files
		if checkAbilities(args.inputdir):
			inputDir = args.inputdir
		else:
			print('The input direcotry does not contain any YAML files.')
			raise SystemExit

		# Check the output directory
		if args.outputdir:
			outputDir = args.outputdir
		else:
			outputDir = os.path.join(os.path.split(os.path.dirname(inputDir))[0], 'abilities-updated/')

		if not os.path.exists(outputDir):
			os.makedirs(outputDir)
			logging.debug('Output directory created: {}'.format(outputDir))
		else:
			logging.debug('Output directory exists: {}'.format(outputDir))

		# Check for existing YAML files
		if checkAbilities(outputDir):
			answer = query_yes_no('The output directory already contains YAML files. If you continue, these files will be overwritten. Would you like to continue?')
			if answer == False:
				print('You chose not to continue. Please double-check your work and try again if needed.')
				raise SystemExit

		# Validate the CSV file
		if args.csv:
			if checkCSVFile(args.csv):
				main(inputDir, outputDir, args.csv)
			else:
				parser.print_help(sys.stderr)
				print('The provided CSV path could not be validated.')
				raise SystemExit
		else:
			parser.print_help(sys.stderr)
			print('You must supply a valid CSV file.')
			raise SystemExit
	else:
		parser.print_help(sys.stderr)
		print('You must provide an input directory containg the YAML files that need to be updated.')
		raise SystemExit
