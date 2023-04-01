
import requests
import pyodide_http
from pyodide.ffi import create_proxy


URL = "http://http://oja89.pythonanywhere.com"
URL = "http://127.0.0.1:5000"


def add_button(text):
  parent = js.document.getElementById("test_div")
  btn = js.document.createElement("button")
  btn.classList = "bg-green-500 hover:bg-green-500 text-gray-800 font-bold py-1 px-2 rounded-l"
  btn.setAttribute('id', 'btnx')
  btn.innerText = text
  #Element("btnx", btn).element.addEventListener("click",  create_proxy(add_button))
  Element("btnx", btn).element.addEventListener("click",  create_proxy(get_next))
  parent.append(btn)

def get_next(asdf):
  response = requests.get(URL + "/api/games")
  controls = response.json()["@controls"]
  for control in controls:
    print(control)
"""
MAIN CODE
"""

# Patch the Requests library so it works with Pyscript
# pyodide_http.patch()
pyodide_http.patch_all()  # new name...


# Make a request to the API
response = requests.get(URL + "/api/")


# Print all from "@controls"
controls = response.json()["@controls"]
for control in controls:
    print(control)
    add_button(control)
