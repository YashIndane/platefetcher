//Getting the p-tags where numbers will be written
b1 = document.getElementById("b1");
b2 = document.getElementById("b2");
b3 = document.getElementById("b3");
b4 = document.getElementById("b4");
b5 = document.getElementById("b5");
b6 = document.getElementById("b6");
b7 = document.getElementById("b7");
b8 = document.getElementById("b8");
b9 = document.getElementById("b9");
b10 = document.getElementById("b10");
numplatebox = document.getElementById("numplate");

//Animation time in ms
var delay = 250;

//Result font color
var colour = "green";


//Updates the detected plate image on webpage
function updateImage(){

    var xhrv = new XMLHttpRequest();
    var valQueryString = "/valsfetch";
    xhrv.open("GET", valQueryString, true);
    xhrv.send();

    xhrv.onload = function(){
        var vals = xhrv.responseText;
        var valsArray = vals.split(" ");

        var bucketresponse = valsArray[0];
        var regionresponse = valsArray[1];

        //Building the url for detected plate stored in S3
        var image_url = "https://".concat(bucketresponse, ".s3.", regionresponse, ".amazonaws.com/detected_plate.png");
        
        //Updating the image
        numplatebox.src = image_url;
        
    }
}


const DEF_DELAY = 1000;
function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms || DEF_DELAY));
}


//This function puts the number on screen
function fun(a,b,c,d,e,f,g,h,i,j){
        
      
    (async()=>{
          
          
          b1.innerHTML = a;
          await sleep(delay);
          b2.innerHTML = b;
          await sleep(delay);
          b3.innerHTML = c;
          await sleep(delay);
          b4.innerHTML = d;
          await sleep(delay);
          b5.innerHTML = e;
          await sleep(delay);
          b6.innerHTML = f;
          await sleep(delay);
          b7.innerHTML = g;
          await sleep(delay);
          b8.innerHTML = h;
          await sleep(delay);
          b9.innerHTML = i;
          await sleep(delay);
          b10.innerHTML = j;
          await sleep(delay);

          b1.style.color = colour;
          b2.style.color = colour;
          b3.style.color = colour;
          b4.style.color = colour;
          b5.style.color = colour;
          b6.style.color = colour;
          b7.style.color = colour;
          b8.style.color = colour;
          b9.style.color = colour;
          b10.style.color = colour;

          

    })()

}


/*This function continously sends GET request to numberfetch API 
  that gets the number written in the number.txt file*/
function fetchNumber(){

          var xhr = new XMLHttpRequest();
          var queryString = "/numberfetch";
          xhr.open("GET", queryString, true);
          xhr.send();

          xhr.onload = function(){

              var response = xhr.responseText;
              if (response === "0"){}
              else{
                console.log(response);
                updateImage();
                fun(response.substr(0,1), response.substr(1,1), response.substr(2,1), response.substr(3,1), response.substr(4,1), response.substr(5,1), response.substr(6,1),response.substr(7,1),response.substr(8,1), response.substr(9,1));
              }
          }
}


//Interval time in ms
var fetchTime = 250;

//Sending the GET requests at regular intervals
fetchNumber();
setInterval(fetchNumber, fetchTime);