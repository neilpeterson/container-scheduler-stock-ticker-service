# Stock App - Container Demo

This is simple stock report application; the end user work flow is:

- User enters a stock symbol or multiple stock symbols and an email address.
- Beast Mode can be used to generate multiple executions (containers).
- User receives a simple stock report via email.

The purpose of this application is to demonstrate the benefits of container technology when paired with distributed application architecture and at scale.

## Architecture

![](./media/stock-app.png)

## Prerequisites

- Azure Storage Queue
- Gmail account configured to allow SMTP access (link).

## Configuration 

Gather the following Items:

- Azure Storage Account Name
- Azure Queue Connection String (see this article)
- Azure Queue Name
- Azure Queue Key
- Docker Host IP Address
- Stock Report Image Name
- Gmail Account Name
- Gmail Password

## Demo

![](./media/stock-app.gif)


