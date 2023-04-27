import json

import requests
import pyodide_http
from pyodide.ffi.wrappers import add_event_listener

# URL = "http://oja89.pythonanywhere.com"
URL = "http://127.0.0.1:5000"
APIKEYHEADER = {"BGT-Api-Key": "asdf"}



def refresh_page(href):
    print("Loading new page")

    # get and jsonify directly
    response = sess.get(URL + href).json()

    # reload controls
    get_controls(response)
    #get_items(response)
    get_contents(response)
    print(f"resp {response}")


def add_control(ctrl, controls):
    print("----add control-button")
    parent = js.document.getElementById("controls")
    btn = js.document.createElement("button")

    btn.setAttribute('id', ctrl)
    btn.setAttribute('class', 'py-button')

    btn.textContent = ctrl

    # cleaner way to add listener: https://jeff.glass/post/pyscript-why-create-proxy/
    # add_event_listener(btn, "click", click_control(href))) # nice but fires automatically

    def click_control(event):
        """
        Way to get around the autofire...
        """
        print(f"CLICKED CONTROL: {ctrl}")
        method = controls[ctrl].get("method")
        href = controls[ctrl].get("href")
        # if it is not just a get ...
        if method == "GET":
            refresh_page(href)
        if method == "DELETE":
            add_choice_buttons(method, href)
        elif method == "POST":
            # get empty forms according to the schema

            add_choice_buttons(method, href)

        elif method == "PUT":
            pass
            # similar to post, but read existing values into form
        else:
            # probably just get...
            refresh_page(href)

    add_event_listener(btn, "click", click_control)
    parent.append(btn)


def add_item(name, href):
    print("----add item-button")
    parent = js.document.getElementById("content")
    btn = js.document.createElement("button")

    btn.setAttribute('id', name)
    btn.setAttribute('class', 'py-button')

    btn.textContent = name

    # cleaner way to add listener: https://jeff.glass/post/pyscript-why-create-proxy/
    # add_event_listener(btn, "click", click_control(href))) # nice but fires automatically

    def click_item(event):
        """
        Way to get around the autofire...
        """
        print(f"CLICKED ITEM: {name}")
        refresh_page(href)

    add_event_listener(btn, "click", click_item)

    parent.append(btn)

def add_choice_buttons(method, href):
    # add cancel (self) and "method"

    parent = js.document.getElementById("controls")
    parent.innerHTML = ""

    # self == cancel?
    c_btn = js.document.createElement("button")
    c_btn.setAttribute('id', "cancel")
    c_btn.setAttribute('class', 'py-button')
    c_btn.textContent = "cancel"

    def click_cancel(event):
        # self?
        refresh_page(href)

    add_event_listener(c_btn, "click", click_cancel)
    parent.append(c_btn)

    # delete
    d_btn = js.document.createElement("button")
    d_btn.setAttribute('id', method)
    d_btn.setAttribute('class', 'py-button')
    d_btn.textContent = method

    def click_submit(event):
        resp = sess.request(method, URL + href)
        output(f"Status: {resp}")
        # TODO: jump to collection instead?
        refresh_page(href)

    add_event_listener(d_btn, "click", click_submit)
    parent.append(d_btn)




def get_controls(response):
    parent = js.document.getElementById("controls")
    parent.innerHTML = ""

    # add buttons for all from "@controls"
    controls = response.get("@controls")
    print("---get new controls")
    for ctrl in controls:
        # don't put profile, it's not working
        if ctrl not in ["profile"]:
            add_control(ctrl, controls)


def get_contents(response):
    """
    Update the contents
    """
    print("---get new content")

    # create element
    # show them on the screen using display
    # https://github.com/pyscript/pyscript/blob/main/docs/reference/API/display.md

    # clear content
    parent = js.document.getElementById("content")
    parent.innerHTML = ""
    # use key name and value to add all to html
    # except controls

    # for each row create and add elements
    for field, props in response.items():
        if field in ["item"]:  # single item
            output(field.upper())
            # TODO: Take these from schema instead so we get empty ones too
            for key, value in props.items():
                # add KEY before as a text:
                output(key)

                input = js.document.createElement("input")

                input.setAttribute('id', key)
                input.setAttribute('class', 'py-box')
                input.setAttribute('value', value)

                input.textContent = value
                parent.append(input)

        if field in ["items", "matches", "maps", "rulesets", "player_results", "team_results"]:  # list of items
        # if field == "items":  # list of items
            # as this is a list inside, we need to go deeper
            # don't use forms here
            output(field.upper())
            # first get the item button
            for i in props:
                for field2, props2 in i.items():
                    # add first the item button
                    if field2 in ["name", "date", "player", "team"]:
                        add_item(props2, i["@controls"]["self"].get("href"))
                    # print everything else (but not controls)
                    if field2 != "@controls":
                        output(f"{field2}: {props2}")

        if field in ["edit"]:
            output(props)


def output(stuff):
    display(stuff, target="content", append=True)


"""
MAIN CODE
"""

# Patch the Requests library, so it works with Pyscript
# pyodide_http.patch()
pyodide_http.patch_all()  # new name...

# create Session to use
with requests.Session() as sess:
    sess.headers.update(APIKEYHEADER)

    # get first data
    refresh_page("/api/")
