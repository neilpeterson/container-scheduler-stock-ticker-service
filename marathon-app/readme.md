# Start container stock via DCOS API

## These two will start the app:

dcos marathon app add https://raw.githubusercontent.com/neilpeterson/container-stock-app-service/master/marathon-app/stock-front.json
dcos marathon app add https://raw.githubusercontent.com/neilpeterson/container-stock-app-service/master/marathon-app/stock-worker-service.json

## Does not need to be started:
dcos marathon app add https://raw.githubusercontent.com/neilpeterson/container-stock-app-service/master/marathon-app/stock-report-service.json