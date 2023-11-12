# Simple Company Management App

A demo app is deployed on [Render](https://simple-company-management-app.onrender.com).
<br>Please use following usernames and passwords to access demo administrator and worker pages.
Demo Administrator Access:
- both username and password: demo_admin

Demo Worker Access:
- both username and password: demo_worker

A simple company management app, targeting a small company, to track and visualize the working hours and sales for each worker. 
It has the following functionalities:
- Admins can create new accounts for their workers
- Admins can check workers' details, working status, total sales, contribution and efficiency
- Workers report working status from their own dashboard
- In the same dashboard, workers can also check his working hours, total sales, and working efficiency


Details on Architecture / Tech stacks:
- serverless architecture, uses SQLite
- Flask, as web application framework
- Flask-Login, to manage user authentication
- SQL Alchemy, for ORM
- HTML, CSS, and vanilla JS for the frontend