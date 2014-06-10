#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Mon script de post installation Xubuntu 14.04 LTS
# Francise par Bristow
# Syntax: # sudo ./xubuntupostinstall-14.04.sh
#
# Nicolargo (aka) Nicolas Hennion
# http://www.nicolargo.com
# Distributed under the GPL version 3 license
#

"""
Post installation script for Xubuntu 14.04 LTS
"""

import os, sys, platform, getopt, shutil, logging, getpass, ConfigParser

# Global variables
#-----------------------------------------------------------------------------

_VERSION="0.6b"
_DEBUG = 1
_LOG_FILE = "/tmp/ubuntu-14.04-postinstall.log"
_CONF_FILE = "https://raw.githubusercontent.com/hypolite-dev/client_linux_scribe/master/xubuntu_14.04_postinstall.cfg"

# System commands
#-----------------------------------------------------------------------------

_APT_ADD = "add-apt-repository -y"
_APT_INSTALL = "DEBIAN_FRONTEND=noninteractive apt-get -y -f install"
_APT_REMOVE = "DEBIAN_FRONTEND=noninteractive apt-get -y -f remove"
_APT_UPDATE = "DEBIAN_FRONTEND=noninteractive apt-get -y update"
_APT_UPGRADE = "DEBIAN_FRONTEND=noninteractive apt-get -y upgrade"
_APT_KEY = "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys"
_WGET = "wget"

#Pouvoir installer des paquets DEB
_DPKG_INSTALL = "dpkg -i"

#Decompresser une archive zip

# Classes
#-----------------------------------------------------------------------------

class colors:
	RED = '\033[91m'
	GREEN = '\033[92m'
	BLUE = '\033[94m'
	ORANGE = '\033[93m'
	NO = '\033[0m'

	def disable(self):
		self.RED = ''
		self.GREEN = ''
		self.BLUE = ''
		self.ORANGE = ''
		self.NO = ''

# Functions
#-----------------------------------------------------------------------------

def init():
	"""
	Init the script
	"""
	# Globals variables
	global _VERSION
	global _DEBUG

	# Set the log configuration
	logging.basicConfig(
		filename=_LOG_FILE,
		level=logging.DEBUG,
		format='%(asctime)s %(levelname)s - %(message)s',
	 	datefmt='%d/%m/%Y %H:%M:%S',
	 )

def syntax():
	"""
	Print the script syntax
	"""
	print "Ubuntu 14.04 post installation script version %s" % _VERSION
	print ""
	print "Syntax: ubuntu-14.04-postinstall.py [-c cfgfile] [-h] [-v]"
	print "  -c cfgfile: Use the cfgfile instead of the default one"
	print "  -h        : Print the syntax and exit"
	print "  -v        : Print the version and exit"
	print ""
	print "Exemples:"
	print ""
	print " # ubuntu-14.04-postinstall.py"
	print " > Run the script with the default configuration file"
	print "   %s" % _CONF_FILE
	print ""
	print " # ubuntu-14.04-postinstall.py -c ./myconf.cfg"
	print " > Run the script with the ./myconf.cfg file"
	print ""
	print " # ubuntu-14.04-postinstall.py -c http://mysite.com/myconf.cfg"
	print " > Run the script with the http://mysite.com/myconf.cfg configuration file"
	print ""

def version():
	"""
	Print the script version
	"""
	sys.stdout.write ("Script version %s" % _VERSION)
	sys.stdout.write (" (running on %s %s)\n" % (platform.system() , platform.machine()))

def isroot():
	"""
	Check if the user is root
	Return TRUE if user is root
	"""
	return (os.geteuid() == 0)

def showexec(description, command, exitonerror = 0, presskey = 0, waitmessage = ""):
	"""
	Exec a system command with a pretty status display (Running / Ok / Warning / Error)
	By default (exitcode=0), the function did not exit if the command failed
	"""

	if _DEBUG: 
		logging.debug ("%s" % description)
		logging.debug ("%s" % command)

	# Wait message
	if (waitmessage == ""):
		waitmessage = description

	# Manage very long description
	if (len(waitmessage) > 65):
		waitmessage = waitmessage[0:65] + "..."
	if (len(description) > 65):
		description = description[0:65] + "..."

	# Display the command
	if (presskey == 1):
		status = "[ ENTER ]"
	else:	
		status = "[En cours]"
	statuscolor = colors.BLUE
	sys.stdout.write (colors.NO + "%s" % waitmessage + statuscolor + "%s" % status.rjust(79-len(waitmessage)) + colors.NO)
	sys.stdout.flush()

	# Wait keypressed (optionnal)
	if (presskey == 1):
		try:
			input = raw_input
		except: 
			pass
		raw_input()

	# Run the command
	returncode = os.system ("/bin/sh -c \"%s\" >> /dev/null 2>&1" % command)

	# Display the result
	if ((returncode == 0) or (returncode == 25600)):
		status = "[  OK   ]"
		statuscolor = colors.GREEN
	else:
		if exitonerror == 0:
			status = "[Warning]"
			statuscolor = colors.ORANGE
		else:
			status = "[ Erreur ]"
			statuscolor = colors.RED

	sys.stdout.write (colors.NO + "\r%s" % description + statuscolor + "%s\n" % status.rjust(79-len(description)) + colors.NO)

	if _DEBUG: 
		logging.debug ("Returncode = %d" % returncode)

	# Stop the program if returncode and exitonerror != 0
	if ((returncode != 0) & (exitonerror != 0)):
		if _DEBUG: 
			logging.debug ("Forced to quit")
		exit(exitonerror)

def getpassword(description = ""):
	"""
	Read password (with confirmation)
	"""
	if (description != ""): 
		sys.stdout.write ("%s\n" % description)

	password1 = getpass.getpass("Password: ");
	password2 = getpass.getpass("Password (confirm): ");

	if (password1 == password2):
		return password1
	else:
		sys.stdout.write (colors.ORANGE + "[Warning] Password did not match, please try again" + colors.NO + "\n")
		return getpassword()

def getstring(message = "Enter a value: "):
	"""
	Ask user to enter a value
	"""
	try:
		input = raw_input
	except: 
		pass
	return raw_input(message)

def waitenterpressed(message = "Press ENTER to continue..."):
	"""
	Wait until ENTER is pressed
	"""
	try:
		input = raw_input
	except: 
		pass
	raw_input(message)
	return 0

def main(argv):
	"""
	Main function
	"""
	try:
		opts, args = getopt.getopt(argv, "c:hv", ["config", "help", "version"])
	except getopt.GetoptError:
		syntax()
		exit(2)

	config_file = ""
	config_url = _CONF_FILE
	for opt, arg in opts:
		if opt in ("-c", "--config"):
			if arg.startswith("http://") or \
				arg.startswith("https://") or \
				arg.startswith("ftp://"):
				config_url = arg
			else:
				config_file = arg
		elif opt in ("-h", "--help"):
			syntax()
			exit()
		elif opt in ('-v', "--version"):
			version()
			exit()

	# Are your root ?
	if (not isroot()):
		showexec ("Script should be run as root", "tpastroot", exitonerror = 1)

	# Is it trusty tahr ?
	_UBUNTU_VERSION = platform.linux_distribution()[2]
	if (_UBUNTU_VERSION != "trusty"):
		showexec ("Script seulement pour Ubuntu 14.04", "tpassoustrusty", exitonerror = 1)

	# Read the configuration file
	if (config_file == ""):
		config_file = "/tmp/ubuntu_14.04_postinstall.cfg"
		showexec ("Telechargement du fichier de configuration", "rm -f "+config_file+" ; "+_WGET+" -O "+config_file+" "+config_url)		
	config = ConfigParser.RawConfigParser()
	config.read(config_file)

	if (config.has_section("gnome3") and config.has_section("unity")):
		showexec ("Can not use both Gnome 3 and Unity, please change your .cfg file", "gnome3etunitygrosboulet", exitonerror = 1)		

	# Parse and exec pre-actions
	for action_name, action_cmd in config.items("preactions"):
		showexec ("Execution de la preaction "+action_name.lstrip("action_"), action_cmd)

	# Parse and installation des depots
	pkg_list_others = {}
	for item_type, item_value in config.items("repos"):
		if (item_type.startswith("ppa_")):
			showexec ("Installation du depot "+item_type.lstrip("ppa_"), _APT_ADD+" "+item_value)
		elif (item_type.startswith("url_")):
			showexec ("Installation du depot "+item_type.lstrip("url_"), _APT_ADD+" \\\"deb "+item_value+"\\\"")
		elif (item_type.startswith("key_")):
			showexec ("Installation de la cle pour le "+item_type.lstrip("key_")+" depot", _APT_KEY+" "+item_value)
		elif (item_type.startswith("pkg_")):
			pkg_list_others[item_type] = item_value

	# Mise a jour des depots
	showexec ("Mise a jour des depots", _APT_UPDATE)

	# Upgrade system
	showexec ("Mise a jour du systeme, soit patient...", _APT_UPGRADE)

	# Activation licence JAVA
	showexec ("Activation licence Java...", "echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections")

	# Activation licence EULA pour les polices Microsoft
	showexec ("Activation licence Polices MS...", "echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | sudo /usr/bin/debconf-set-selections")


	# Parse and install packages
	for pkg_type, pkg_list in config.items("packages"):
		if (pkg_type.startswith("remove_")):
		    showexec ("Suppression des paquets "+pkg_type.lstrip("remove_"), _APT_REMOVE+" "+pkg_list)
		else:
		    showexec ("Installation des paquets "+pkg_type, _APT_INSTALL+" "+pkg_list)

	# Installation des paquets des dépôts
	#~ print pkg_list_others
	for pkg in pkg_list_others.keys():
		showexec ("Installation des paquets des depots "+pkg, _APT_INSTALL+" "+pkg_list_others[pkg])

	# Allow user to read DVD (CSS)
	showexec ("DVDs CSS encryption reader", "sh /usr/share/doc/libdvdread4/install-css.sh")

	# Download and install dotfiles: vimrc, prompt...
	if (config.has_section("dotfiles")):
		# Create the bashrc.d subfolder
		showexec ("Create the ~/.bashrc.d subfolder", "mkdir -p $HOME/.bashrc.d")
		if (config.has_option("dotfiles", "bashrc")):
			showexec ("Install bash main configuration file", _WGET+" -O $HOME/.bashrc "+config.get("dotfiles", "bashrc"))
		if (config.has_option("dotfiles", "bashrc_prompt")):
			showexec ("Install bash prompt configuration file", _WGET+" -O $HOME/.bashrc.d/bashrc_prompt "+config.get("dotfiles", "bashrc_prompt"))
		if (config.has_option("dotfiles", "bashrc_aliases")):
			showexec ("Install bash aliases configuration file", _WGET+" -O $HOME/.bashrc.d/bashrc_aliases "+config.get("dotfiles", "bashrc_aliases"))
		# Vim
		if (config.has_option("dotfiles", "vimrc")):
			showexec ("Install the Vim configuration file", _WGET+" -O $HOME/.vimrc "+config.get("dotfiles", "vimrc"))

		# Htop
		if (config.has_option("dotfiles", "htoprc")):
			showexec ("Install the Htop configuration file", _WGET+" -O $HOME/.htoprc "+config.get("dotfiles", "htoprc"))


	# Installation des paquets deb en installant ligne par ligne
	for pkg_type, pkg_list in config.items("debs"):
		showexec ("Telechargement de "+pkg_type, _WGET+" -O /tmp/"+pkg_type+".deb "+pkg_list)
		showexec ("Installation du paquet "+pkg_type, _DPKG_INSTALL+" /tmp/"+pkg_type+".deb")


	# Resolution des problemes de dependances
	showexec ("Resolution pb dependances", _APT_INSTALL)



	# Gnome 3 configuration
	if (config.has_section("gnome3")):
		# Set the default theme
		if (config.has_option("gnome3", "theme")):
			showexec ("Set the default Gnome Shell theme to "+config.get("gnome3", "theme"), "gsettings set org.gnome.desktop.interface gtk-theme "+config.get("gnome3", "theme"))
		# Set the default icons
		if (config.has_option("gnome3", "icons")):
			showexec ("Set the default Gnome Shell icons to "+config.get("gnome3", "icons"), "gsettings set org.gnome.desktop.interface icon-theme "+config.get("gnome3", "icons"))
		# Set the default cursors
		if (config.has_option("gnome3", "cursors")):
			showexec ("Set the default Gnome Shell cursors to "+config.get("gnome3", "cursors"), "gsettings set org.gnome.desktop.interface cursor-theme "+config.get("gnome3", "cursors"))
		# Download and install the default Conky configuration
		if (config.has_option("gnome3", "conky")):
			showexec ("Install the Conky configuration file", _WGET+" -O $HOME/.conkyrc "+config.get("gnome3", "conky"))
		# Get the minimize/maximize button and ALT-F2 shortcut back
		showexec ("Get the minimize and maximize button back in Gnome Shell", "gconftool-2 -s -t string /desktop/gnome/shell/windows/button_layout \":minimize,maximize,close\"")
		showexec ("Get ALT-F2 back to me", "gconftool-2 --recursive-unset /apps/metacity/global_keybindings")
		# Gnome Shell is the default UI
		showexec ("Gnome Shell is now the default shell", "/usr/lib/lightdm/lightdm-set-defaults -s gnome-shell")

	# Unity configuration
	if (config.has_section("unity")):
		# Set the default theme
		if (config.has_option("unity", "theme")):
			showexec ("Set the default Unity theme to "+config.get("unity", "theme"), "gsettings set org.gnome.desktop.interface gtk-theme "+config.get("unity", "theme"))
		# Set the default icons
		if (config.has_option("unity", "icons")):
			showexec ("Set the default Unity icons to "+config.get("unity", "icons"), "gsettings set org.gnome.desktop.interface icon-theme "+config.get("unity", "icons"))
		# Set the default cursors
		if (config.has_option("unity", "cursors")):
			showexec ("Set the default Unity cursors to "+config.get("unity", "cursors"), "gsettings set org.gnome.desktop.interface cursor-theme "+config.get("unity", "cursors"))
		# Download and install the default Conky configuration
		if (config.has_option("unity", "conky")):
			showexec ("Install the Conky configuration file", _WGET+" -O $HOME/.conkyrc "+config.get("unity", "conky"))
		# Unity is the default UI
		showexec ("Unity is now the default shell", "/usr/lib/lightdm/lightdm-set-defaults -s unity-3d")

	# Parse and exec post-actions
	for action_name, action_cmd in config.items("postactions"):
		showexec ("Execute postaction "+action_name.lstrip("action_"), action_cmd)

	# End of the script
	print("---")
	print("Fin du script.")
	print(" - Cfg du fichier : "+config_file)
	print(" - Log du Fichier : "+_LOG_FILE)
	print("")
	print("Merci de redemarrer la session pour terminer.")
	print("---")

# Main program
#-----------------------------------------------------------------------------

if __name__ == "__main__":
	init()
	main(sys.argv[1:])
	exit()
