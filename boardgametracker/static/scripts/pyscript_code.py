import json

import requests
import pyodide_http
from pyodide.ffi.wrappers import add_event_listener

# URL = "http://oja89.pythonanywhere.com"
URL = "http://127.0.0.1:5000"
APIKEYHEADER = {"BGT-Api-Key": "asdf"}


def add_button(ctrl, controls):
    print("----add control-button")
    parent = js.document.getElementById("controls")
    btn = js.document.createElement("button")

    # use py-click
    # https://docs.pyscript.net/latest/tutorials/py-click.html
    # btn.setAttribute('py-click', "click_control('asd')")
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
        method = controls[ctrl]["method"]
        href = controls[ctrl]["href"]
        # if it is not just a get ...
        if method == "GET":
            refresh_page(href=href)
        elif method == "DELETE":
            add_choice_buttons(method, href)
        elif method == "POST":
            # get empty forms according to the schema

            add_choice_buttons(method, href)

        elif method == "PUT":
            pass
            # similar to post, but read existing values into form
        else:
            print(f"WEIRD METHOD: {method}")
            pass

    add_event_listener(btn, "click", click_control)
    parent.append(btn)


def add_choice_buttons(method, href):
    # add cancel (self) and "method"
    # dont use add_button

    parent = js.document.getElementById("controls")
    parent.innerHTML = ""

    # self == cancel?
    c_btn = js.document.createElement("button")
    c_btn.setAttribute('id', "cancel")
    c_btn.setAttribute('class', 'py-button')
    c_btn.textContent = "cancel"


    def click_cancel(event):
        # get self
        # update controls (it updates all)
        #update_controls(href=href)
        refresh_page(href=href)

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
        refresh_page(href=href)


    add_event_listener(d_btn, "click", click_submit)
    parent.append(d_btn)


def add_items(name, href):
    print("----add item-button")
    parent = js.document.getElementById("items")
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
        refresh_page(href=href)

    add_event_listener(btn, "click", click_item)

    parent.append(btn)



def refresh_page(href):

    response = sess.get(URL + href)

    # reload controls
    get_controls(response)
    get_items(response)
    get_contents(response)


def get_controls(response):
    parent = js.document.getElementById("controls")
    parent.innerHTML = ""

    # Print all from "@controls"
    controls = response.json()["@controls"]
    print("---get new controls")
    for ctrl in controls:
        # not items pls
        # name, url, method?
        # name = ctrl
        # href = controls[ctrl]["href"]
        # # check if there is a method
        # try:
        #     method = controls[ctrl]["method"]
        # except KeyError:
        #     print("no method, default to get")
        #     method = "GET"
        add_button(ctrl, controls)


def get_items(response):
    print("---get new items")

    # clear existing items
    parent = js.document.getElementById("items")
    parent.innerHTML = ""

    # buttons for all items (works for all collections but matches?)
    try:
        items = response.json()["items"]
        # add new buttons
        for item in items:
            # add buttons for items
            # name = item["name"] # doesn't work if not named
            name = item.get("name")
            if name is None:
                # works for matches:
                name = item.get("date")
            href = item["@controls"]["self"]["href"]
            add_items(name, href)
    except KeyError as kerr:
        # we are probably looking at one item, so no items...
        pass


def get_contents(response):
    """
    Update the contents
    """
    print("---get new content")

    results = response.json()
    # create element
    # show them on the screen using display
    # https://github.com/pyscript/pyscript/blob/main/docs/reference/API/display.md

    # clear content
    parent = js.document.getElementById("content")
    parent.innerHTML = ""
    # use key name and value to add all to html
    # except controls

    # for each row create and add elements
    for field, props in results.items():
        if field in ["item"]:  # single item
            output(field.upper())
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
            # as this is a list inside, we need to go deeper
            # don't use forms here
            output(field.upper())
            for i in props:
                for field2, props2 in i.items():
                    if field2 not in ["@controls"]:
                        output(f"{field2}: {props2}")


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
