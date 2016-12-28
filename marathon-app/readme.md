# Start container stock via DCOS API

## These two will start the app:

dcos marathon app add https://raw.githubusercontent.com/neilpeterson/container-stock-app-service/master/marathon-app/stock-front-lb.json

dcos marathon app add https://raw.githubusercontent.com/neilpeterson/container-stock-app-service/master/marathon-app/stock-worker-service.json

## Does not need to be started:
dcos marathon app add https://raw.githubusercontent.com/neilpeterson/container-stock-app-service/master/marathon-app/stock-report-service.json

## Some other helpful commands

- dcos marathon app list
- dcos marathon task list
- dcos task log <app>