import requests
import pyodide_http
from pyodide.ffi.wrappers import add_event_listener

# URL = "http://oja89.pythonanywhere.com"
URL = "http://127.0.0.1:5000"
APIKEYHEADER = {"BGT-Api-Key": "asdf"}


def add_button(name, href, method):
    print("----add control-button")
    parent = js.document.getElementById("controls")
    btn = js.document.createElement("button")

    # use py-click
    # https://docs.pyscript.net/latest/tutorials/py-click.html
    # btn.setAttribute('py-click', "click_control('asd')")
    btn.setAttribute('id', name)
    btn.setAttribute('class', 'py-button')

    btn.textContent = name

    # cleaner way to add listener: https://jeff.glass/post/pyscript-why-create-proxy/
    # add_event_listener(btn, "click", click_control(href))) # nice but fires automatically

    def click_control(event):
        """
      Way to get around the autofire...
      """
        print(f"CLICKED CONTROL: {name}")

        # if it is not just a get ...
        if method == "GET":
            update_controls(href=href)
        else:
            print(f"THIS WAS NOT A GET, but {method}")
            # probably this needs then to show the contents in a form?
            make_form(name, href, method)

    add_event_listener(btn, "click", click_control)
    parent.append(btn)


def make_form(name, href, method):
    print("----add form")
    # get the parent
    parent = js.document.getElementById("forms")
    # get the existing data

    lista = ["asd", "dads"]

    # for each row create and add elements
    for field in lista:
        input = js.document.createElement("input")

        input.setAttribute('id', field)
        input.setAttribute('class', 'py-box')
        input.setAttribute('value', 'sometext')

        input.textContent = name
        parent.append(input)

    # add submit button
    btn = js.document.createElement("button")
    btn.setAttribute('id', method)
    btn.setAttribute('class', 'py-button')
    btn.textContent = method
    parent.append(btn)

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
        update_items(href=href)

    add_event_listener(btn, "click", click_item)

    parent.append(btn)


def delete_all_controls():
    """
    Delete the control buttons shown.
    """
    print("---delete old control buttons")
    parent = js.document.getElementById("controls")
    parent.innerHTML = ""


def delete_all_items():
    """
    Delete the item buttons shown.
    """
    print("---delete old item buttons")
    parent = js.document.getElementById("items")
    parent.innerHTML = ""


def update_controls(response=None, href=None):
    """
    Clicked control button or..
    href is None -> was item
    response is None -> was ctrl
    """
    print("--updating control buttons")
    if response is None:
        response = sess.get(URL + href)
        print(f"----updating controls because control clicked: {response.json()}")
        # update items
        update_items(response=response)
    if href is None:
        response = response
        print("----updating controls because item clicked")
    # remove old ctrls
    delete_all_controls()
    # add new controls
    get_controls(response)


def update_items(response=None, href=None):
    """
    Clicked item button or..
    href is None -> was ctrl
    response is None -> was item
    """
    print("--updating item buttons")
    if response is None:
        response = sess.get(URL + href)
        print(f"----updating items because item clicked:: {response.json()}")
        # update controls
        update_controls(response=response)
    if href is None:
        response = response
        print("----updating items because control clicked")
    # remove old items
    delete_all_items()
    # add new items
    get_items(response)

    # also update contents
    update_contents(response)


def update_contents(response=None):
    """
    Clicked item?
    """
    print("--updating contents")
    get_results(response)


def get_entrance():
    # Make the first request to the API
    response = sess.get(URL + "/api/")
    print("GET ENTRANCE")
    get_controls(response)


def get_controls(response):
    # Print all from "@controls"
    controls = response.json()["@controls"]
    print("---get new controls")
    for ctrl in controls:
        # not items pls
        # name, url, method?
        name = ctrl
        href = controls[ctrl]["href"]
        # check if there is a method
        try:
            method = controls[ctrl]["method"]
        except KeyError:
            print("no method, default to get")
            method = "GET"
        add_button(name, href, method)


def get_items(response):
    print("---get new items")
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


def get_results(response):
    """
    Update the contents
    """
    print("---get new content")

    results = response.json()
    # create element
    # show them on the screen using display
    # https: // github.com / pyscript / pyscript / blob / main / docs / reference / API / display.md

    # clear display
    display("", target="results", append=False)

    # use key name and value to add all to html
    # except controls

    # from https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/exercise-4-implementing-hypermedia-clients/#to-put-or-not
    for field, props in results.items():
        if field in ["item"]:  # single item
            for key, value in props.items():
                output(f"{key}: {value}")
        if field in ["items"]:  # list of items
            # as this is a list inside, we need to go deeper
            for i in props:
                for field2, props2 in i.items():
                    if field2 not in ["@controls"]:
                        output(f"{field2}: {props2}")


def output(stuff):
    display(stuff, target="results", append=True)


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
    get_entrance()
