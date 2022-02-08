# Country Risk Tool

A Django 2 project designed to assess risks in various areas for certain countries (2019). 

## Getting Started
Python version: 3.7.5

Clone project:
```
git clone https://github.com/pymaster13/country_risk_tool.git && cd country_risk_tool
```

Create and activate virtual environment:
```
python3 -m venv venv && source venv/bin/activate
```

Install libraries:
```
python3 -m pip install -r requirements.txt
```

Run local Django server:
```
python3 manage.py runserver
```
## Functional

The project was implemented for a foreign customer. He provided several templates that should be loaded and on the basis of which the necessary tables should be built and certain calculations should be made. 
Requirements from the customer:
- For working of site: It is neccessary log in on site as admin. Go to "Upload" page. Then add 3 files (metrics, data_inputs, valuation) .csv or .xls to data base. Need start to upload with metrics.csv(xls).
- After filling of data base you and other users can go to "Select" page - main page of app.
- As admin you may add users in "Admin panel" page. You can give any user admin permissions - need choose user in admin page and check box "is_staff".
- As admin you can delete template(session in DB).
- As authenticated user you can not go to "Admin panel", but any pages are opened for you.
- As simple user you can view only start page with information about app.

