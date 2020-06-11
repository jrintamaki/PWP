'''
Client for the frolftracker API. 

Some functions are borrowed from lovelace exercise 4.
'''


import json
import requests

API_URL = "localhost:5000"

# NOTE: This is borrowed from Lovelace exercise 4: "mumeta_submit.py". Credit to Mika Oja
class APIError(Exception):
    """
    Exception class used when the API responds with an error code. Gives
    information about the error in the console.    
    """

    def __init__(self, code, error):
        """
        Initializes the exception with *code* as the status code from the response
        and *error* as the response body.
        """
    
        self.error = json.loads(error)
        self.code = code
        
    def __str__(self):
        """
        Returns all details from the error response sent by the API formatted into
        a string.
        """

        return "Error {code} while accessing {uri}: {msg}\nDetails:\n{msgs}".format(
            code=self.code,
            uri=self.error["resource_url"],
            msg=self.error["@error"]["@message"],
            msgs="\n".join(self.error["@error"]["@messages"])
        )

def create_player(name):
    pass

def create_course(name, holes=18, par=54):
    pass

def create_score(throws, player_id, course_id):
    pass

def modify_player(name):
    pass

def modify_course(name, holes=18, par=54):
    pass

def modify_score(throws, player_id, course_id):
    pass

def delete_player(id):
    pass

def delete_course(id):
    pass

def delete_score(id):
    pass

def iterate_players(s, root_path, players_href):
    pass

def iterate_courses(s, root_path, courses_href):
    pass

def iterate_scores(s, root_path, scores_href):
    pass

def find_player_href(name, collection):
    pass

def find_course_href(name, collection):
    pass

def find_score_href(name, collection):
    pass


# NOTE: This is borrowed from Lovelace exercise 4: "mumeta_submit.py". Credit to Mika Oja
def submit_data(s, ctrl, data):
    """
    submit_data(s, ctrl, data) -> requests.Response
    
    Sends *data* provided as a JSON compatible Python data structure to the API
    using URI and HTTP method defined in the *ctrl* dictionary (a Mason @control).
    The data is serialized by this function and sent to the API. Returns the 
    response object provided by requests.
    """
    
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp

#if __name__ == "__main__":
#    with requests.Session() as s:
#        resp = s.get(API_URL + "/api/sensors/")
#        body = resp.json()
#        prompt_from_schema(s, body["@controls"]["senhub:add-sensor"])