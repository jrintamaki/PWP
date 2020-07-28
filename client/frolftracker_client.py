"""
Client for the frolftracker API.
"""

import curses

import json
import requests

from pick import pick
API_URL = "http://localhost:5000"

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


def get_players_href(s):
    resp = s.get(API_URL + '/api')
    body = resp.json()
    return body['@controls']['frolf:players-all']['href']

def get_courses_href(s):
    resp = s.get(API_URL + '/api')
    body = resp.json()
    return body['@controls']['frolf:courses-all']['href']

def get_scores_href(s):
    resp = s.get(API_URL + '/api')
    body = resp.json()
    return body['@controls']['frolf:scores-all']['href']

def get_scores(s):
    scores_href = get_scores_href(s)
    resp = s.get(API_URL + scores_href)
    body = resp.json()
    scores = body['items']
    ret = []
    for score in scores:
        throws = str(score['throws'])
        date = score['date']
        player = get_player_by_id(s, str(score['player_id']))['name']
        course = get_course_by_id(s, str(score['course_id']))['name']
        ret.append({'id' : str(score['score_id']), 'throws' : throws, 'date' : date,
            'player' :  player, 'course' : course, 'player_id' : score['player_id'], 'course_id' : score['course_id']})

    return ret

def get_score_by_id(s, id):
    scores_href = get_scores_href(s)
    resp = s.get(API_URL + scores_href + id)
    body = resp.json()

    return body

def get_player_by_id(s, id):
    players_href = get_players_href(s)
    resp = s.get(API_URL + players_href + id)
    body = resp.json()

    return body

def get_course_by_id(s, id):
    courses_href= get_courses_href(s)
    resp = s.get(API_URL + courses_href + id)
    body = resp.json()

    return body

def delete_score_by_id(s, id):
    scores_href = get_scores_href(s)
    resp = s.get(API_URL + scores_href + id)
    body = resp.json()
    do_request(s, body['@controls']['frolf:delete'])


def find_player_href(name, collection):
    pass

def find_course_href(name, collection):
    pass

def find_score_href(name, collection):
    pass

def get_values_for_pick(option):
    return str("{} {} {} {}").format(option['throws'], option['date'], option['course'], option['player'])

def convert_value(value, schema_props):
    if schema_props["type"] == "integer":
        value = int(value)
    if schema_props["type"] == "number":
        value = float(value)
    return value

def prompt_from_schema_edit(s, ctrl):
    body = {}
    schema = ctrl['@controls']['edit']['schema']
    for field in schema['required']:
        props = schema['properties'][field]
        cur_value = ctrl[field]
        out = prompt(props["description"] + ': ', cur_value)
        if not out:
            out = cur_value
        val = convert_value(out, props)
        body[field] = val
    resp = do_request(s, ctrl['@controls']['edit'], body)
    if resp.status_code == 204:
        pass
    else:
        raise APIError(resp.status_code, resp.content)

def prompt_from_schema(s, ctrl):
    body = {}
    schema = ctrl["schema"]
    for field in schema["required"]:
        props = schema["properties"][field]
        out = prompt(props["description"] + ': ')
        val = convert_value(out, props)
        body[field] = val
    resp = do_request(s, ctrl, body)
    if resp.status_code == 201:
        return resp.headers["Location"]
    raise APIError(resp.status_code, resp.content)

# NOTE: This is borrowed from Lovelace exercise 4: "mumeta_submit.py". Credit to Mika Oja
def do_request(s, ctrl, data=None):
    if data:
        resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    else:
        resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
    )
    return resp

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

def scores_menu(s):
    title = "Choose action"
    options = ["Get scores", "Add score", "Edit score", "Delete score", "Return",]

    option, _ = pick(options, title)

    scores_href = get_scores_href(s)
    body = s.get(API_URL + scores_href).json()
    scores = get_scores(s)
    if option == "Get scores":
        try:
            option, _ = pick(scores, "Press enter to continue.", indicator='', options_map_func=get_values_for_pick)
        except ValueError:
            prompt("No scores. \n   Enter to continue")
    elif option == "Add score":
        prompt_from_schema(s, body["@controls"]["frolf:add-score"])
        prompt("Success! \n   Enter to continue")
    elif option == "Edit score":
        option, _ = pick(scores, "Select score to edit", options_map_func=get_values_for_pick)
        body = s.get(API_URL + scores_href + option['id']).json()
        prompt_from_schema_edit(s, body)
        prompt("Success! \n   Enter to continue")
    elif option == "Delete score":
        option, _ = pick(scores, "Select score to edit", options_map_func=get_values_for_pick)
        delete_score_by_id(s, option['id'])
    elif option == "Return":
        pass

def players_menu(s):
    title = "Choose action"
    options = ["Get players", "Add player", "Edit player", "Delete player", "Get scores by player", "Return",]

    option, _ = pick(options, title)
    players_href = get_players_href(s)
    body = s.get(API_URL + players_href).json()
    if option == "Get players":
        prompt("Not implemented")
    elif option == "Add player":
        prompt_from_schema(s, body["@controls"]["frolf:add-player"])
        prompt("Success! \n   Enter to continue")
    elif option == "Edit player":
        prompt("Not implemented")
    elif option == "Delete player":
        prompt("Not implemented")
    elif option == "Get scores by player":
        prompt("Not implemented")
    elif option == "Return":
        pass

def courses_menu(s):
    title = "Choose action"
    options = ["Get courses", "Add course", "Edit course", "Delete course", "Get scores by course", "Return",]

    option, _ = pick(options, title)
    courses_href = get_courses_href(s)
    body = s.get(API_URL + courses_href).json()

    if option == "Get courses":
        prompt("Not implemented")
    elif option == "Add course":
        prompt_from_schema(s, body["@controls"]["frolf:add-course"])
        prompt("Success! \n   Enter to continue")
    elif option == "Edit course":
        prompt("Not implemented")
    elif option == "Delete course":
        prompt("Not implemented")
    elif option == "Get scores by course":
        prompt("Not implemented")
    elif option == "Return":
        pass


def prompt(ps=None, value=''):
    stdscr = curses.initscr()
    stdscr.clear()
    curses.echo()
    stdscr.addstr(2, 3, ps)
    stdscr.addstr(3, 3, str(value))
    stdscr.refresh()
    ret = stdscr.getstr(2 + 1, 3, 20).decode(encoding="utf-8")
    curses.endwin()
    return ret

def main():
    with requests.Session() as s:
        while True:
            title = "Welcome to frolftracker!"
            options = ["Scores", "Players", "Courses", "Exit"]
            option, _ = pick(options, title)

            title = "Choose action"
            if option == "Scores":
                scores_menu(s)
            elif option == "Players":
                players_menu(s)
            elif option == "Courses":
                courses_menu(s)
            elif option == "Exit":
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("K'bye")
