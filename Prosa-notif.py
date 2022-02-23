# Importing libraries
import requests
from bs4 import BeautifulSoup, Comment
import hashlib
import json
from win10toast import ToastNotifier

# Data has the following form
# new_data {
# 	event_elems: Contains each event element as soup
#	headers: Contains the events header text
# 	hash: Contains the hash of the headers
# }


def extract_new_data(soup):
    # Strip html of comments
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]

    new_data = {}
    # Extract all event elements
    new_data['event_elems'] = soup.find(id='eventList').findChild()
    # Extract all event headers
    new_data['headers'] = get_headers(new_data['event_elems'])
    # Create hash
    hash_string = '&'.join(new_data['headers'])
    new_data['hash'] = get_hash(hash_string)

    return new_data


def get_headers(event_elems):
    headers = []
    header_elems = event_elems.find_all('h3')
    for header_elem in header_elems:
        headers.append(header_elem.find('span').text)

    return headers


def get_hash(string):
    return hashlib.sha224(string.encode()).hexdigest() + "b"


def load_file_data_to_dict(filename):
    with open(filename) as json_file:
        return json.load(json_file)


def changes_detected(new_data, old_data):
    if(old_data['hash'] != new_data['hash']):
        return True
    return False


def print_event_changes(old_data, new_data):
    new_events_found = False
    old_headers = old_data['headers']
    new_headers = new_data['headers']

    print("Event changes has been made!")
    toaster = ToastNotifier()
    for header in new_headers:
        if header not in old_headers:
            new_events_found = True
            msg = "New event found: " + header
            print(msg)
            toaster.show_toast(msg, icon_path=None)
    if not new_events_found:
        print("Events have been removed but not created.")


def save_new_data(data):
    data['event_elems'] = str(data['event_elems'])
    with open("data.json", "w") as outfile:
        json.dump(data, outfile)


url = 'https://www.prosa.dk/arrangementer/'
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')
new_data = extract_new_data(soup)
old_data = load_file_data_to_dict('data.json')
if changes_detected(new_data, old_data):
    print_event_changes(old_data, new_data)
    save_new_data(new_data)
else:
    print("No changes detected.")
