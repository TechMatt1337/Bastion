# importing the requests library 
import requests

# api-endpoint
URL = "http://ec2-18-223-248-15.us-east-2.compute.amazonaws.com/api"

# location given here
location = "delhi technological university"

# defining a params dict for the parameters to be sent to the API
PARAMS = {'lastupdate':0}

# sending get request and saving the response as response object
r = requests.get(url = URL, params = PARAMS)

# extracting data in json format
data = r.json()

print(data)
