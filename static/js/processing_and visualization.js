window.onload = function(){
  can_request_data = true; // wait until the page has fully loaded so that people counts can be processed
}

const request_inventory_count_frequency_ms = 1000; // sets the frequency of the collecting and analyzing inventory counts
var can_request_data = false;
const request_inventory_count_url = './get_inventory_counts';
var bottle = 0; //variables to store No of bounding boxes received from the request
var box_drink = 0;

var bottle_count = document.getElementById("bottle_count"); // spans counts of items
var box_drink_count = document.getElementById("box_drink_count");

var bottle_border = document.getElementById("bottle"); // used to set colors of the gauges
var box_drink_border = document.getElementById("box_drink");

function fetch_inventory_count(){ // gets count of drinks from python
  fetch(request_inventory_count_url)
    .then((response) => response.json())
    .then((data) => 
      {
        console.log(data);
        bottle = data['bottle'];
        box_drink = data['box_drink'];

        console.log("-------------------------------------------------------------");
        console.log("bottle : " + bottle);
        console.log("box_drink : " + box_drink);
        console.log("-------------------------------------------------------------");  

        show_inventory_counts();

      }
    ); 
}

function show_inventory_counts(){ // show counts on html page
  bottle_count.innerHTML = bottle
  bottle_count.style.display = "block";

  box_drink_count.innerHTML = box_drink
  box_drink_count.style.display = "block";

  // check if no bounding boxes are found 
  if (isNaN(bottle) && isNaN(box_drink)){
    // display borderes with black color
    set_default_border_colors();
  }
  else{ //set border colors based on count
    set_border_colors();
  }
}


function set_border_colors(){ // sets the border colors wrt the number of counts

  // from a survery, 7 out of 10 people preferred bottled drinks to box/carton drinks
  if (bottle > box_drink){
    bottle_border.style.borderColor = "green";
    box_drink_border.style.borderColor = "orange"; 
  }

  else if (bottle < box_drink){
    bottle_border.style.borderColor = "red"; // show red/warning when bottle drinks are less
    box_drink_border.style.borderColor = "orange"; 
  }

  else {
    bottle_border.style.borderColor = "orange";
    box_drink_border.style.borderColor = "orange";
  }

  // -----------------------------------------------------------------
 
  // reset counts
  bottle = 0;
  box_drink = 0;
}

function set_default_border_colors(){
  console.log("setting circle borders to default color")
  bottle_border.style.borderColor = "#14151A";
  box_drink_border.style.borderColor = "#14151A";
}

function foo() {
  if (can_request_data){
    fetch_inventory_count();
  }
  setTimeout(foo, request_inventory_count_frequency_ms); // obtain people counts every second
}
foo();