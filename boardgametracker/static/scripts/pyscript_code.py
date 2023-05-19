import json

import requests
import pyodide_http
from pyodide.ffi.wrappers import add_event_listener

# URL = "http://oja89.pythonanywhere.com"
URL = "http://127.0.0.1:5000"
APIKEYHEADER = {"BGT-Api-Key": "asdf"}



def refresh_page(href):
    #print("Loading new page")

    # get and jsonify directly
    response = sess.get(URL + href).json()

    # reload controls
    get_controls(response)
    #get_items(response)
    get_contents(response)
    #print(f"resp {response}")


def add_control(ctrl, controls):
    #print("----add control-button")
    parent = js.document.getElementById("controls")
    btn = js.document.createElement("button")

    btn.setAttribute('id', ctrl)
    btn.setAttribute('class', 'py-button')

    btn.textContent = ctrl


    def click_control(event):
        """
        Way to get around the autofire...
        """
        #print(f"CLICKED CONTROL: {ctrl}")
        method = controls[ctrl].get("method")
        href = controls[ctrl].get("href")
        # if it is not just a get ...
        if method == "GET":
            refresh_page(href)
        if method == "DELETE":
            add_choice_buttons(method, href)
        elif method == "POST":
            # get empty forms according to the schema

            # cannot GET any page
            # so we need to build the boxes
            # but we can get schema

            props = controls[ctrl]["schema"].get("properties")

            # clear contents first
            parent = js.document.getElementById("content")
            parent.innerHTML = ""

            # print title (what are we adding)
            output(ctrl.upper())

            for key in props:
                #add key as text
                output(key)

                input = js.document.createElement("input")

                input.setAttribute('id', key)
                input.setAttribute('class', 'py-box')
                input.setAttribute('value', '')

                input.textContent = ''
                parent.append(input)

            add_choice_buttons(method, href)

        elif method == "PUT":

            # get all forms according to the schema
            # data exists, but there might be empty fields that are not showing

            props = controls[ctrl]["schema"].get("properties")

            # clear contents first
            parent = js.document.getElementById("content")
            parent.innerHTML = ""

            # print title (what are we adding)
            output(ctrl.upper())

            # get existing data
            resp = sess.request("GET", URL + href).json()

            print(resp)
            print(resp.items())
            print(resp["item"])
            # get schema
            for field in props:
                #add field as text
                output(field)

                input = js.document.createElement("input")

                input.setAttribute('id', field)
                input.setAttribute('class', 'py-box')

                # fill existing values in
                input.setAttribute('value', resp["item"][field])

                parent.append(input)

            add_choice_buttons(method, href)


        else:
            # probably just get...
            refresh_page(href)

    add_event_listener(btn, "click", click_control)
    parent.append(btn)


def add_item(name, href):
    #print("----add item-button")
    parent = js.document.getElementById("content")
    btn = js.document.createElement("button")

    btn.setAttribute('id', name)
    btn.setAttribute('class', 'py-button')

    btn.textContent = name


    def click_item(event):
        """
        Way to get around the autofire...
        """
        #print(f"CLICKED ITEM: {name}")
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
        if method == "DELETE":
            resp = sess.request(method, URL + href)
            output(f"Status: {resp}")
            if resp.status_code == 204:
                #TODO: get collection
                #now just jump to entry
                refresh_page("/api/")
            refresh_page(href)

        if method in ["POST", "PUT"]:
            # get data from the input boxes
            data_raw= {}
            boxes = js.document.getElementsByClassName("py-box")
            for box in boxes:
                #output(box.id) # Key
                #output(box.value) # inputted value
                data_raw[box.id] = box.value

            #output(data_raw) # {'name': 'asd}

            resp = sess.request(
                method,
                URL + href,
                data=json.dumps(data_raw),
                headers = {"Content-type": "application/json"}
            )
            output(f"Status: {resp}")

            # if successful, refresh to location
            if resp.status_code in [201, 204]:
                output(resp.headers)
                refresh_page(resp.headers["Location"])



    add_event_listener(d_btn, "click", click_submit)
    parent.append(d_btn)




def get_controls(response):
    parent = js.document.getElementById("controls")
    parent.innerHTML = ""

    # add buttons for all from "@controls"
    controls = response.get("@controls")
    #print("---get new controls")
    for ctrl in controls:
        # don't put profile, it's not working
        if ctrl not in ["profile"]:
            add_control(ctrl, controls)


def get_contents(response):
    """
    Update the contents
    """
    #print("---get new content")

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
            for key, value in props.items():
                output(f"{key}: {value}")

        if field in ["items", "matches", "maps", "rulesets", "player_results", "team_results"]:  # list of items
            # as this is a list inside, we need to go deeper
            # don't use forms here

            output(f"{field.upper()} related to this")
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
