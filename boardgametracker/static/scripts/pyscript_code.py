
import requests
import pyodide_http
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import add_event_listener


# URL = "http://http://oja89.pythonanywhere.com"
URL = "http://127.0.0.1:5000"


def add_button(name, href):
  parent = js.document.getElementById("navigation")
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
      update_controls(href)

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
        update_items(href)

    add_event_listener(btn, "click", click_item)

    parent.append(btn)
def delete_all_buttons():
    """
    Delete the control buttons shown.
    """
    parent = js.document.getElementById("navigation")
    parent.innerHTML = ""

def delete_all_items():
    """
    Delete the item buttons shown.
    """
    parent = js.document.getElementById("items")
    parent.innerHTML = ""


def update_controls(href):
    #print(href)
    response = requests.get(URL + href)

    # remove old buttons
    delete_all_buttons()

    # add new controls
    get_controls(response)

    # get items
    #get_items(response)
    update_items(response)


def update_items(response):
    #response = requests.get(URL + href)

    delete_all_items()

    get_items(response)


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
    # buttons for all items (works for all but matches?)
    items = response.json()["items"]

    # add new buttons
    for item in items:
        # add buttons for items
        name = item["name"]
        href = item["@controls"]["self"]["href"]
        add_items(name, href)





"""
MAIN CODE
"""

# Patch the Requests library so it works with Pyscript
# pyodide_http.patch()
pyodide_http.patch_all()  # new name...

# get first data
get_entrance()
