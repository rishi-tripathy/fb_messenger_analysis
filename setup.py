import os
import re
from pprint import pprint

from helpers import get_json, count_messages, check_participants

BASE_DIR = "/home/zaibo/code/fb_analysis/data"
MY_NAME = "Zaibo Wang"

# To look at groupchats, use find_groupchat() by adding your conditions to narrow down the search
# Then, add them to the GROUPCHATS list
GROUPCHATS = [
    # (name, path)
    ("situation_room", "/home/zaibo/code/fb_analysis/data/thesituationroom_69ae5d10b1/message.json"),
    ("eggplant", "/home/zaibo/code/fb_analysis/data/96a68cd96d/message.json")
]

def generate_friends(n=50):
    """
    Generate friends.py which is used by most of the other scripts
    friends.py will contain paths to the top n most frequently messaged friends
    """
    all_paths = []
    for dir in os.listdir(BASE_DIR):
        if dir.startswith("."): # Macs have a .DS_STORE file which throws an exception
            continue
        inner_dir = BASE_DIR + "/" + dir
        for filename in os.listdir(inner_dir):
            if filename == "message.json":
                filepath = inner_dir + "/" + filename
                all_paths.append(filepath)

    # Each element is a tuple of (friend_name, total_messages)
    messages_per_friend = []

    for path in all_paths:
        message_json = get_json(path)
        if check_participants(message_json):
            messages = message_json.get("messages", [])
            participant = message_json.get("participants")[0]
            total_messages = count_messages(messages)
            if total_messages != 0:
                messages_per_friend.append((participant, total_messages, path))
    messages_per_friend.sort(key=lambda x: x[1], reverse=True)

    # People have weird names, this regex can break...
    name_pattern = "(?P<first_name>([A-Z]|-)*) (?P<last_name>([A-Z]|-)*)"
    with open("friends.py", "w") as f:
        names_and_paths = []
        paths = []
        for name, _, path in messages_per_friend[:n]:
            name = name.upper()
            regex = re.match(name_pattern, name)
            if not regex:
                continue
            parsed_name = "_".join([regex.group("first_name"), regex.group("last_name")])
            parsed_name = parsed_name.replace(" ", "_")
            parsed_name = parsed_name.replace("-", "_")
            write_wrapper(f, parsed_name, path)
            names_and_paths.append((name, path))
            paths.append(path)
        f.write("ALL_FRIENDS = %s\n" % str(names_and_paths))
        f.write("ALL_FRIEND_PATHS = %s\n" % str(paths))

def generate_groupchats():
    """
    Use find_groupchat() to get groupchat paths and hardcode them to this function
    to append them to the end of friends.py
    """
    with open("friends.py", "a") as f:
        for name, path in GROUPCHATS:
            write_wrapper(f, name, path)

def find_groupchat():
    """
    generate will not generate group chats, so we must find them manually
    We can set up conditions to narrow down the chats (ex: find all groupchats with 15+ people)
    """
    all_paths = []
    for dir in os.listdir(BASE_DIR):
        inner_dir = BASE_DIR + "/" + dir
        for filename in os.listdir(inner_dir):
            if filename == "message.json":
                filepath = inner_dir + "/" + filename
                all_paths.append(filepath)

    for path in all_paths:
        message_json = get_json(path)
        party = message_json.get("participants", "")
        # Make some condition to look for group chats
        if len(party) > 15:
            print(path)

def generate_name():
    with open("friends.py", "a") as f:
        write_wrapper(f, "MY_NAME", MY_NAME)

def write_wrapper(f, variable, value):
    f.write("%s = \"%s\"\n" % (variable, value))

generate_friends(50)
generate_groupchats()
generate_name()