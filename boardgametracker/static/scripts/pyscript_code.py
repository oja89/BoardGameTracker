
import requests
import pyodide_http
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import add_event_listener


# URL = "http://http://oja89.pythonanywhere.com"
URL = "http://127.0.0.1:5000"


def add_button(name, href):
  parent = js.document.getElementById("navigation")
  btn = js.document.createElement("button")
  btn.classList = "bg-green-500 hover:bg-green-500 text-gray-800 font-bold py-1 px-2 rounded-l"

  # use py-click
  # https://docs.pyscript.net/latest/tutorials/py-click.html
  #btn.setAttribute('py-click', "click_control('asd')")
  btn.setAttribute('id', name)
  btn.setAttribute('class', 'py-button')

  btn.textContent = name

  # cleaner way to add listener: https://jeff.glass/post/pyscript-why-create-proxy/
  # add_event_listener(btn, "click", click_control(href))) # nice but fires automatically
  def click_function(event):
      """
      Way to get around the autofire...
      """
      click_control(href)

  add_event_listener(btn, "click", click_function)

  parent.append(btn)

def delete_all_buttons():
    """
    Delete the buttons shown.
    """
    # they are under test_div
    parent = js.document.getElementById("navigation")
    parent.innerHTML = ""


def click_control(href):
    print(href)
    response = requests.get(URL + href)

    # remove old buttons
    delete_all_buttons()

    # add new controls:
    get_controls(response)

def get_entrance():
    # Make a request to the API
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


"""
MAIN CODE
"""

# Patch the Requests library so it works with Pyscript
# pyodide_http.patch()
pyodide_http.patch_all()  # new name...

# get first data
get_entrance()
