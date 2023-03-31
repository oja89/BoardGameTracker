"use strict";

const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}

function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

function playerRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderPlayer)'>show</a>";

    return "<tr><td>" + item.name +
            "</td><td>" + link + "</td></tr>";
}

function appendPlayerRow(body) {
    $(".resulttable tbody").append(playerRow(body));
}

function getSubmittedPlayer(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendPlayerRow);
    }
}

function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}

function submitPlayer(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.name = $("input[name='name']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedPlayer);
}

function renderPlayerForm(ctrl) {
    let form = $("<form>");
    let name = ctrl.schema.properties.name;
    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitPlayer);
    form.append("<label>" + name.description + "</label>");
    form.append("<input type='text' name='name'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}

function renderPlayer(body) {
    $("div.navigation").html(
        "<a href='" +
        body["@controls"].collection.href +
        "' onClick='followLink(event, this, renderPlayers)'>collection</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();
    renderPlayerForm(body["@controls"].edit);
    $("input[name='name']").val(body.name);
    $("form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
}

function renderPlayers(body) {
    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<tr><th>Name</th><th>Model</th><th>Location</th><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(playerRow(item));
    });
    renderPlayerForm(body["@controls"]["BGT:add-player"]);
}

$(document).ready(function () {
    getResource("http://localhost:5000/api/players/", renderPlayers);
});
