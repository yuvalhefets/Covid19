from flask import Flask, request, jsonify
import json
import requests
import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

DAYS_BACK = "30"
COVID19_BASE = "https://disease.sh/v3/covid-19/historical/?lastdays="+DAYS_BACK
DB = "covid_countries.json"
DEATHS_PEAK = "deathsPeak"
NEW_CASES_PEAK = "newCasesPeak"
RECOVERED_PEAK = "recoveredPeak"
SUCCESS_MSG = "success"
FAIL_MSG = "fail"
SUCCESS_CODE = 200


def write_json(data, filename=DB):
    """
    writes given data to json file
    :param data: dictionary to add to json file
    :param filename: json file
    :return:
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def get_date():
    """
    returns the current date in mm\dd\yy format
    :return: current date
    """
    today = datetime.datetime.now()
    return today.strftime("%x")


def current_data():
    """
    returns current json data in dictionary format
    :return: json data
    """
    json_file = open(DB, "r")
    data = json.load(json_file)
    json_file.close()

    return data


def parse_values(cases, deaths, recovered):
    """
    calculates requested value of covid data
    :param cases: list of cases number of the past 20 days
    :param deaths: list of deaths number of the past 20 days
    :param recovered: list of recovered number of the past 20 days
    :return: maximum of each of the lists
    """
    return max(cases), max(deaths), max(recovered)


def create_entry(country):
    """
    creates a new entry in the json file for a given country
    :param country: entry key
    :return: requested values for cases, recovered and deaths
    """
    cases = list(country["timeline"]["cases"].values())
    recovered = list(country["timeline"]["recovered"].values())
    deaths = list(country["timeline"]["deaths"].values())

    cases_value, deaths_value, recovered_value = parse_values(
        cases, deaths, recovered)
    return {"cases": cases_value, "recovered": deaths_value, "deaths": recovered_value}


def request_records():
    """
    sends an HTTP request to an API asking for last 30 days covid data
    and saves the results to the json file
    """
    r = requests.get(COVID19_BASE)
    json_data = r.json()
    with open(DB) as json_file:
        data = json.load(json_file)
        data["date"] = get_date()
        for country in json_data:
            country_lower_case = country["country"].lower()
            data[country_lower_case] = create_entry(country)

    write_json(data)


def parse_record(country, method, data):
    """
    read an entry from the json file and returns it's required structure
    as what should be returned from this service
    :param country: desired country
    :param method: desired method (cases, deaths, recovered)
    :param data: current json data
    :return:
    """
    output = {"country": country,
              "method": method,
              "date": data["date"]}

    if method == NEW_CASES_PEAK:
        output["value"] = data[country]['cases']
    elif method == RECOVERED_PEAK:
        output["value"] = data[country]['recovered']
    elif method == DEATHS_PEAK:
        output["value"] = data[country]['deaths']

    return output


def get_data(country, method):
    """
    reads the required data from the json file.
    if date has changed, sends a new request for updated covid data
    :param country: desired country
    :param method: desired method (cases, deaths, recovered)
    :return:
    """
    data = current_data()
    if country not in data:
        return jsonify({})
    if data['date'] != get_date():
        request_records()
        data = current_data()

    return jsonify(parse_record(country, method, data))


@app.before_first_request
def before_first_request():
    write_json({})
    request_records()


@app.route('/newCasesPeak', methods=['GET'])
def cases_peak():
    country = request.args.get('country', default='', type=str)
    return get_data(country, NEW_CASES_PEAK)


@app.route('/recoveredPeak', methods=['GET'])
def recoveredPeak():
    country = request.args.get('country', default='', type=str)
    return get_data(country, RECOVERED_PEAK)


@app.route('/deathsPeak', methods=['GET'])
def deathsPeak():
    country = request.args.get('country', default='', type=str)
    return get_data(country, DEATHS_PEAK)


@app.route('/status', methods=['GET'])
def status_endpoint():
    r = requests.get(COVID19_BASE)
    result = {}
    if r.status_code == SUCCESS_CODE:
        result["status"] = SUCCESS_MSG
    else:
        result["status"] = FAIL_MSG
    return jsonify(result)


@app.errorhandler(404)
def not_found(e):
    return {}


if __name__ == "__main__":
    app.run()
