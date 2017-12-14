dj_mdm
=======

# Overview

MDM is usually implemented with the use of a third party product that has management features for particular vendors of mobile devices.
The project aims for setting up a simple iOS Mobile Device Management Server(MDM Server).

## Clone the Source

    # Clone Dj_Init repository
    git clone https://github.com/agnihotri7/dj_mdm.git dj_mdm

## Configure It

    # update required files
    replace dj_mdm/hideApps.txt, dj_mdm/unhideApps.txt, dj_mdm/server-ssl.csr, dj_mdm/apnsCert.pem with your own certificates
Follow steps given in the [link](https://github.com/project-imas/mdm-server/blob/master/README.md) to get required Certificates to run MDM Server.

    # install requirements.txt under your virtual env.
    pip install -r requirements.txt

    # migrate database
    ./manage.py migrate

    # runserver
    ./manage.py runserver
