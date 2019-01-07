var x,y
// The name tag of the selection fields to validate.
var firstName = "missions-0-M14 - Meteoroid Deflection-0-2"
var secondName = "missions-0-M14 - Meteoroid Deflection-0-3"

// Takes in the select object.
function validateInput(dropdown) {
    if (dropdown.name == firstName) {
        // Take the text from select option and parse to an integer.
        x = parseInt(dropdown.options[dropdown.selectedIndex].text, 10);
    } else if (dropdown.name == secondName){
        y = parseInt(dropdown.options[dropdown.selectedIndex].text, 10);
    }
    // Only 2 Meteoroids allowed, alert judge and reset last option.
    if (x+y > 2){
        alert("There are a maximum of 2 Meteoroids")
        dropdown.selectedIndex = "0";
    }
  }
