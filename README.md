client_linux_scribe
===================

ceci est un simple hébergement du travail disponible ici : https://raw.githubusercontent.com/dane-lyon/clients-linux-scribe/

il a pour but de me permettre de télécharger les fichiers de configuration post install modifié

Scripts pour Client Scribe (x)Ubuntu 12.04 ou 14.04

Ce script permet d'intégrer (x)Ubuntu 12.04 ou 14.04 dans un environnement Eole-Scribe 2.2 ou 2.3.

Il est plutôt adapté à Unity mais adaptable éventullement pour d'autres environnements graphiques.

Avant de lancer ce script, assurez-vous d'avoir installé toutes vos applications, puis vous pouvez cloner vos postes avec la solution libre OSCAR

Télécharger le script, exemple pour le client Ubuntu 14.04 : wget https://raw.githubusercontent.com/dane-lyon/clients-linux-scribe/master/client_scribe_ubuntu_14.04.sh
Se placer dans le répertoire courant puis lancer les commandes :

chmod +x client_scribe_ubuntu_14.04.sh

sudo ./client_scribe_ubuntu_14.04.sh

Remarques :

Script de post-installation

Pour gagner du temps lors de la création du poste modèle, on pourra utiliser un script de post-installation qui installera le système avec toutes les applications souhaitées : https://github.com/bristow/ubuntupostinstall

Personnalisation des valeurs par défaut

vous pouvez éditer les valeurs par défaut en début de script afin de les adapter à votre environnement.

Personnalisation des menus

Pour personnaliser le menu à tous les utilisateurs, chercher dans le script ces lignes :

echo "[com.canonical.indicator.session]
user-show-menu=false
[org.gnome.desktop.lockdown]
disable-user-switching=true
disable-lock-screen=true
[com.canonical.Unity.Launcher]
favorites=[ 'nautilus-home.desktop', 'firefox.desktop','libreoffice-startcenter.desktop', 'gcalctool.desktop','gedit.desktop','gnome-screenshot.desktop' ]
" > /usr/share/glib-2.0/schemas/my-defaults.gschema.override
La ligne favorites=[ 'nautilus-home.desktop', 'firefox.desktop','libreoffice-startcenter.desktop','gcalctool.desktop','gedit.desktop','gnome-screenshot.desktop' ] est à adapter en fonction de vos besoins :

Pour connaitre le nom des raccourcis, faire dans un terminal : ls /usr/share/applications/

Pour voir à quelle application cela correspond, avec l'explorateur, il faut se déplacer dans /usr/share/applications/

A noter que chaque élève ou enseignant peut personnaliser son menu.

TO DO :

gestion centralisée des profils (navigateurs, session...)
gestion des mises à jour centralisées des postes clients
