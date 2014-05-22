#!/bin/bash
#script d'integration de station mint
#testé avec Scribe 2.3
#
# Run as root, of course.
if [ "$UID" -ne "0" ]
then
  echo "Il faut etre root pour executer ce script. ==> sudo "
  exit 
fi 
. /etc/lsb-release
if [ "$DISTRIB_RELEASE" != "16" ]
then 
	echo " pas Mint Qiana"
	exit
fi

ipscribepardefaut="192.168.0.1"
ipscribe=""
#export http_proxy=""
echo "Donnez l'ip du scribe par défaut : $ipscribepardefaut "
read ipscribe

if [ "$ipscribe" == "" ]
then
 echo "ip non renseignée"
 ipscribe=$ipscribepardefaut
fi
echo "scribe = "$ipscribe

#rendre debconf silencieux
export DEBIAN_FRONTEND="noninteractive"
export DEBIAN_PRIORITY="critical"
#installation des paquets necessaires
apt-get update
apt-get install -y ldap-auth-client  libpam-mount   cifs-utils nscd

#Fichiers de config

# /etc/ldap.conf
echo "
# /etc/ldap.conf
host $ipscribe
base o=gouv, c=fr
nss_override_attribute_value shadowMax 999
" > /etc/ldap.conf

#auth ldap
echo "[open_ldap]
nss_passwd=passwd:  files ldap
nss_group=group: files ldap 
nss_shadow=shadow: files ldap 
nss_netgroup=netgroup: nis
" > /etc/auth-client-config/profile.d/open_ldap
#application de la conf nsswitch
auth-client-config -t nss -p open_ldap
#modules PAM mkhomdir pour pam-auth-update
echo "Name: Make Home directory
Default: yes
Priority: 128
Session-Type: Additional
Session:
        optional                        pam_mkhomedir.so silent
" > /usr/share/pam-configs/mkhomedir
# mise en place de la conf pam.d
pam-auth-update consolekit  ldap  libpam-mount  unix mkhomedir --force

#on remet debconf dans sa conf initiale
export DEBIAN_FRONTEND="dialog"
export DEBIAN_PRIORITY="high" 

#montage des partages scribe avec pam_mount
professeurs="<volume user=\"*\" fstype=\"cifs\" server=\"$ipscribe\" path=\"professeurs\" mountpoint=\"/media/professeurs\" />"
homes="<volume user=\"*\" fstype=\"cifs\" server=\"$ipscribe\" path=\"perso\" mountpoint=\"~/Documents\" />"
#netlogon="<volume user=\"*\" fstype=\"cifs\" server=\"$ipscribe\" path=\"netlogon\" mountpoint=\"/media/netlogon\" />"
eclairng="<volume user=\"*\" fstype=\"cifs\" server=\"$ipscribe\" path=\"eclairng\" mountpoint=\"/media/Poste de travail\" />"
grep "/media/Poste de travail" /etc/security/pam_mount.conf.xml  >/dev/null; if [ $? != 0 ];then sed -i "/<\!-- Volume definitions -->/a\ $eclairng" /etc/security/pam_mount.conf.xml; else echo "eclairng deja present";fi
grep "mountpoint=\"~\"" /etc/security/pam_mount.conf.xml  >/dev/null; if [ $? != 0 ];then sed -i "/<\!-- Volume definitions -->/a\ $homes" /etc/security/pam_mount.conf.xml; else echo "homes deja present";fi
#grep "/media/netlogon" /etc/security/pam_mount.conf.xml  >/dev/null; if [ $? != 0 ];then sed -i "/<\!-- Volume definitions -->/a\ $netlogon" /etc/security/pam_mount.conf.xml; else echo "netlogon deja present";fi
grep "/media/professeurs" /etc/security/pam_mount.conf.xml  >/dev/null; if [ $? != 0 ];then sed -i "/<\!-- Volume definitions -->/a\ $professeurs" /etc/security/pam_mount.conf.xml; else echo "professeurs deja present" ;fi

grep "<cifsmount>mount -t cifs //%(SERVER)/%(VOLUME) %(MNTPT) -o \"noexec,nosetuids,mapchars,cifsacl,serverino,nobrl,iocharset=utf8,user=%(USER),uid=%(USERUID)%(before=\\",\\" OPTIONS)\"</cifsmount>" /etc/security/pam_mount.conf.xml  >/dev/null; if [ $? != 0 ];then sed -i "/<\!-- pam_mount parameters: Volume-related -->/a\ <cifsmount>mount -t cifs //%(SERVER)/%(VOLUME) %(MNTPT) -o \"noexec,nosetuids,mapchars,cifsacl,serverino,nobrl,iocharset=utf8,user=%(USER),uid=%(USERUID)%(before=\\",\\" OPTIONS)\"</cifsmount>" /etc/security/pam_mount.conf.xml; else echo "mount.cifs deja present";fi

#/etc/profile
echo "
export LC_ALL=fr_FR.utf8
export LANG=fr_FR.utf8
export LANGUAGE=fr_FR.utf8
" >> /etc/profile
#ne pas creer les dossiers par defaut dans home
sed -i "s/enabled=True/enabled=False/g" /etc/xdg/user-dirs.conf

# les profs peuvent sudo
grep "%DomainAdmins ALL=(ALL) ALL" /etc/sudoers > /dev/null; if [ $?!=0 ];then sed -i "/%admin ALL=(ALL) ALL/a\%DomainAdmins ALL=(ALL) ALL" /etc/sudoers; else echo "prof deja dans sudo";fi 

#/etc/security/group.conf
grep "*;*;*;Al0000-2400;floppy,audio,cdrom,video,plugdev,scanner" /etc/security/group.conf  >/dev/null; if [ $? != 0 ];then echo "*;*;*;Al0000-2400;floppy,audio,cdrom,video,plugdev,scanner" >> /etc/security/group.conf; else echo "group.conf ok";fi

echo "reboot necessaire"
