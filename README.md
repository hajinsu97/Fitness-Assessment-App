# Fitness Assessment App

A fitness app that merges data from a Google Sheet into a Google Doc.

Example Google Doc template: https://docs.google.com/document/d/1JfYsCbmk1uTGrgC15OFubSjPbbD0hopqv4d0xwOyzOM/edit?usp=sharing

## Local Testing
```
cd ../KBBMA-Fitness-App/
source fitness-app/bin/activate

export GOOGLE_CLIENT_ID=
export GOOGLE_CLIENT_SECRET=
export SECRET_KEY=
export DATABASE_URL=

python app.py

http://127.0.0.1:8080/?doc_url=https%3A%2F%2Fdocs.google.com%2Fdocument%2Fd%2F1JfYsCbmk1uTGrgC15OFubSjPbbD0hopqv4d0xwOyzOM%2Fedit%3Fusp%3Dsharing&sheets_url=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F1yJ7IM1NaNHq2xm7zPgHrV6lcidHhB5_gtVEUx-D7mm8%2Fedit%3Fusp%3Dsharing&sheets_name=2021

```

## App Deployment
```
pip3 freeze > requirements.txt
git push heroku main
```

## Database
```
heroku pg:psql

# Fresh Database
drop schema public cascade;
create schema public;
grant all on schema public to postgres;
grant all on schema public to public;

python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

## Goal
Monitor athletes to maximise the positive effects (eg, fitness, readiness and performance) and minimise the negative effects (eg, excessive fatigue, injury and illness) of training
- ideal performance test and workload ‘metric’ should be sport-specific

## Metric Ideas
- Block speed (cm/s) - time = # frames/framerate -> speed = distance/time
- Endurance - Skipping rope doubles

https://www.topendsports.com/sport/martial-arts/testing.htm

## Examples
![image](https://user-images.githubusercontent.com/70655743/120419803-1fd81200-c331-11eb-9a71-23aa430653e1.png)
![image](https://user-images.githubusercontent.com/70655743/120420137-c58b8100-c331-11eb-9c80-961f7c3f1a19.png)

~~Power BI~~ Can't automate multiple filter values
Zoho free
