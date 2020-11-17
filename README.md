# Covid19

# Descroption
this project consists of a python microservice that fetches certain information
about Covid19 cases in the world.
It is implemented using Flask, and once it runs it gets HTTP requests asking for
some desired information, and returns the data in json format.

# Usage
in order to use the service, the script app.py needs to be run. Requests can be
made in the following syntax (from the browser or cmd):

- curl localhost:8080/status
  returns a value of success/fail to contact the backend API
  
- curl localhost:8080/newCasesPeak?country=<country_name>
  Returns the date (and value) of the highest peak of new
  Covid-19 cases in the last 30 days for a required country.
  
- curl localhost:8080/deathsPeak?country=<country_name>
  Returns the date (and value) of the highest peak of death
  Covid-19 cases in the last 30 days for a required country.

- curl localhost:8080/recoveredPeak?country=<country_name>
  Returns the date (and value) of the highest peak of recovered
  Covid-19 cases in the last 30 days for a required country.
  
- any other request
  returns an empty json object

- return value is in the following format:
  {"country": country, "value": requests number, "date": current date,
   "method": requested method}
   
# Design Choices
- json file
  I chose to save all current date's data in a json file (where the countries are
  the entries) because I figured it would be more efficiant to have to handle
  one request to the backend API every single day. This way, every new request
  for data simply needs to find it localy in the json file.
  Using MongoDB or SQLAlchemy may have been a better choice, but I wanted to keep things
  simple for this project, since I can't assume these things would be installed on any server
  running this app (like jenkins).
  
- functions
  I tried to make this script scalable by creating different function for actions that
  we may want to change in the future. For example, extracting the peak value of the last
  30 days is a behavior that can be easily changed in the parse_value function, and will
  not affect the rest of the service logic.
