function hidden_search_button() {
    if(document.getElementById("search_input").value==="") { 
           document.getElementById("search_button").disabled = true; 
       } else { 
           document.getElementById("search_button").disabled = false;
       }
   }

const stars = document.querySelectorAll(".rating span");

console.log(stars)

