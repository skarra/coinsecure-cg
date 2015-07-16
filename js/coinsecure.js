// 
// Created : Mon Jul 13 23:03:25 IST 2015
//
// Copyright (C) 2015, Sriram Karra <karra.etc@gmail.com>
// All Rights Reserved
//
// Licensed under the GNU AGPL v3
// 

function addDatePickerHandler () {
    $("#from").datepicker({
	defaultDate: "+1w",
	changeMonth: true,
	changeYear: true,
	numberOfMonths: 1,
	dateFormat: "yy-mm-dd",
	onClose: function(selectedDate) {
	    $("#to").datepicker("option", "minDate", selectedDate);
	}
    });

    $("#to").datepicker({
	defaultDate: "+1w",
	changeMonth: true,
	changeYear: true,
	numberOfMonths: 1,
	dateFormat: "yy-mm-dd",
	onClose: function(selectedDate) {
	    $("#from").datepicker("option", "maxDate", selectedDate);
	}
    });
}

function saveAllFormFields () {
    console.log('Saving all form fields to localstorage...');
    localStorage.setItem("cs_apikey", $("#apikey").val());
    localStorage.setItem("cs_from", $("#from").val());
    localStorage.setItem("cs_to", $("#to").val());
    console.log('Saving all form fields to localstorage...done.');
}

function loadFormFields () {
    $("#apikey").val(localStorage.getItem("cs_apikey"));
    $("#from").val(localStorage.getItem("cs_from"));
    $("#to").val(localStorage.getItem("cs_to"));
}

// Register callbacks to handle specific events on our main UI.
function addFormHandlers () {
    console.log('addFormHandlers');

    addDatePickerHandler();

    $("#compute_cg_act").submit(function() {
	saveAllFormFields();
    });

    $("#fetch_txns").submit(function() {
	localStorage.setItem("cs_apikey", $("#apikey").val());
    });

    $("#cgtxns").dataTable();
    $("#buys").dataTable();
    $("#sells").dataTable();
}

function setActiveNav () {
    var pathname = window.location.pathname;;
    console.log('url: ' + pathname);

    if (pathname == '/') {
	$("#nav_brand").addClass("active-nav");
    } else if (pathname == "/transactions") {
	$("#nav_txns").addClass("active-nav");
    } else if (pathname == "/cgActual") {
	$("#nav_cg_act").addClass("active-nav");
    } else if (pathname == "/cgProj") {
	$("#nav_cg_pr").addClass("active-nav");
    }
}

function onLoad () {
    // Initialize the database if available
    addFormHandlers();
    setActiveNav();
    loadFormFields();
}

jQuery(onLoad);
