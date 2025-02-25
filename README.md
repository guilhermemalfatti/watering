# watering
code related to the watering project


TODO:
- run once a day automatically
    - run automatically only if there was not a manual run thru MQTT messaging
- Store the running entries in a local DB like sqllite
- thru aws MQTT cancel the today's auto run
- notification system when we run water
- Thru aws messaging option to stop the plugin, and disconnect from the MQTT


Supervisor commands:
- supervisorctl rereadhttps://www.piawesome.com/how-tos/Supervisor%20as%20a%20Background%20Service%20Manager.html

To update the supervisor config, from the folder /etc/supervisor run
- sudo supervisorctl reread
- sudo supervisorctl update

- sudo supervisorctl restart all