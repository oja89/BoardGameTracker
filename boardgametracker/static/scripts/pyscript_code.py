
import requests
import pyodide_http
from pyodide.ffi.wrappers import add_event_listener


URL = "http://http://oja89.pythonanywhere.com"
# URL = "http://127.0.0.1:5000"


def add_button(name, href):
  parent = js.document.getElementById("controls")
  btn = js.document.createElement("button")

  # use py-click
  # https://docs.pyscript.net/latest/tutorials/py-click.html
  #btn.setAttribute('py-click', "click_control('asd')")
  btn.setAttribute('id', name)
  btn.setAttribute('class', 'py-button')

  btn.textContent = name

  # cleaner way to add listener: https://jeff.glass/post/pyscript-why-create-proxy/
  # add_event_listener(btn, "click", click_control(href))) # nice but fires automatically

  def click_control(event):
      """
      Way to get around the autofire...
      """
      update_controls(href=href)

  add_event_listener(btn, "click", click_control)

  parent.append(btn)


def add_items(name, href):
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
        update_items(href=href)

    add_event_listener(btn, "click", click_item)

    parent.append(btn)


def delete_all_buttons():
    """
    Delete the control buttons shown.
    """
    parent = js.document.getElementById("controls")
    parent.innerHTML = ""


def delete_all_items():
    """
    Delete the item buttons shown.
    """
    parent = js.document.getElementById("items")
    parent.innerHTML = ""


def update_controls(response=None, href=None):
    """
    Clicked control button or..
    href is None -> was item
    response is None -> was ctrl
    """
    if response is None:
        response = requests.get(URL + href)
        # update items
        update_items(response=response)
    if href is None:
        response = response
    # remove old ctrls
    delete_all_buttons()
    # add new controls
    get_controls(response)


def update_items(response=None, href=None):
    """
    Clicked item button or..
    href is None -> was ctrl
    response is None -> was item
    """
    if response is None:
        response = requests.get(URL + href)
        # update controls
        update_controls(response=response)
    if href is None:
        response = response
    # remove old items
    delete_all_items()
    # add new items
    get_items(response)

    # also update contents
    update_contents(response)

def update_contents(response=None, href=None):
    """
    Clicked item?
    """
    get_results(response)


def get_entrance():
    # Make the first request to the API
    response = requests.get(URL + "/api/")
    get_controls(response)


def get_controls(response):
    # Print all from "@controls"
    controls = response.json()["@controls"]
    for ctrl in controls:
        # not items pls
        # name, url, method?
        name = ctrl
        href = controls[ctrl]["href"]
        add_button(name, href)


def get_items(response):
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
        # maybe just print stuff
        print(response.json())

def get_results(response):
    """
    Update the contents
    """
    try:
        results = response.json()
        # results = response.json()["item"]
        # create element
        # show them on the screen using display
        # https: // github.com / pyscript / pyscript / blob / main / docs / reference / API / display.md
        display(results, target="results", append=False)
        # how to use _repr_json???

    except:
        pass

    # use key name and value to add all to html
    # except controls

"""
MAIN CODE
"""

# Patch the Requests library so it works with Pyscript
# pyodide_http.patch()
pyodide_http.patch_all()  # new name...

# get first data
get_entrance()
