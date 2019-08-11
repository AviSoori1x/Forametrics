<script>
    var image = new Image();
    image.src = "{{ url_for('static', filename='loading2.gif') }}"
    image.onload = function () {
      console.log('loading gif is ready to go!'); // remove this in production
    };

    function translate(sourceElem, destElem) {
        $(destElem).html('<center><img src="{{ url_for('static', filename='loading2.gif') }}"></center>');
        $.post('/translate', {
            text: $(sourceElem).val()
        }).done(function(response) {
            $(destElem).text(response['text']);
        }).fail(function() {
            $(destElem).text("{{'Error: Could not contact server.' }}");
        });
    }
</script>

style ="right: 0px;bottom: 0px;"


$('#toTranslate').on('focus',function (e) {
 $('#loadingGif').append('<span><img style ="width:60px; height: 40px;" src="{{ url_for('static', filename='metype.gif') }}"></span>');
});



    $('#toTranslate').click(function(){
        $('#loadingGif').show();

    $(document).not("#toTranslate").click(function() {
        $('#loadingGif').hide();
    });


    $("#loadingGif").append('<span><img style ="right:0px; bottom:0px; width:60px; height: 40px;" src="{{ url_for('static', filename='metype.gif') }}"></span>');

    $("#toTranslate").keypress(function(){
          $('#loadingGif').show();
    });

    ----------------------

        $(document).ready(function () {
        $("body").keypress(function(e) {
          if($(e.target).attr('id') === "toTranslate") {
              $("#loadingGif").show()
          }

          else {
              $("#loadingGif").hide();
          }
        });
      });

      //Get all the missing entities by looping, add that here
      $("#clickButton").hide();
      $("#InfoButton").show();
      let question = 'What is the social network?';
      $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
      $('#InfoButton').click(function(){
        //Some code


      });
      //This
      let obj = eval(response['text']);
      //$(destElem).text(response['text']);
      //$(destElem).text(response['text']+" |Missing entities: "+array_ents[1]+ " |the entire thing: "+array_ents);\
      //let str_obj = JSON.parse(response['text']);
      //$(destElem).text(str_obj['available_entities_dic']);


      //This doesn't fucking work because JS is retarded
      for (var key in obj['missing_ents']) {
          if (missing_entities.hasOwnProperty(key)) {
              //console.log(key + " -> " + p[key]);
              //let ent = JSON.stringify(key);
              $("#clickButton").hide();
              $("#InfoButton").show();
              let question = 'Please provide the ' + obj['missing_ents'][key]+ '.' ;
              $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
              //now this is entering shit in an object when you click the InfoButton
              $('#InfoButton').click(function(){
                  entity_store[key] = $(sourceElem).val();
              });

          }
      }


      //This is entirely new and needs a lot of rework
      let counter = obj['missing_ents'].length;// this is 2 if intent is engagement: period, socialnetwork
      $("#clickButton").hide();
      $("#InfoButton").show();
      let index = 0;
      let question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
      $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
      $('#InfoButton').click(function(){
        if (counter-1> index){//this needs re-work
          entity_store[obj['missing_ents'][index]] = $(sourceElem).val();
          index = index + 1;
          question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
          $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
        }
        else{
          $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+doneMessage+'</p></div>');
          $("#InfoButton").hide();
          $("#refreshButton").show();

        }
      });



      //--------javascript broken--------



      else {
        //This is entirely new and needs a lot of rework
        let count = obj['missing_ents'].length;// this is 2 if intent is engagement: period, socialnetwork
        $("#clickButton").hide();
        $("#InfoButton").show();
        let index = 0;
        let question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
        $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
        if (count> index){
            $('#InfoButton').click(function(){
          //this needs re-work
                entity_store[obj['missing_ents'][index]] = $(sourceElem).val();
                $('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+$(sourceElem).val()+'</p></div>');
                index = index + 1;
            //question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
            //$('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
          });
        };
          else{
            $('#InfoButton').click(function(){
          //this needs re-work
              $("#InfoButton").hide();
              $("#clickButton").show();
                //entity_store[obj['missing_ents'][index]] = $(sourceElem).val();
                //$('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+$(sourceElem).val()+'</p></div>');
                //index = index + 1;
            //question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
            //$('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
          }




        //--------New----Stuff Below inside else does not work --------

      }

  }).fail(function() {
      $(destElem).text("{{'Error: Could not contact server.' }}");
  });
}

// This is the entire else block when it didn't work well.
//This is entirely new and needs a lot of rework
let counter = obj['missing_ents'].length;// this is 2 if intent is engagement: period, socialnetwork
$("#clickButton").hide();
$("#InfoButton").show();
let index = 0;
let question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
$('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
$('#InfoButton').click(function(){
  if (counter > index){
    entity_store[obj['missing_ents'][counter-1]] = $(sourceElem).val();
    counter = counter- 1;
    question = 'Please provide the ' + obj['missing_ents'][counter]+ '.' ;
    $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
  }
  else{
    $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+doneMessage+'</p></div>');
    $("#InfoButton").hide();
    $("#refreshButton").show();

  }
});
//-----------------------------Trying to swap---------------
if (counter > index){
    $('#InfoButton').click(function(){
      entity_store[obj['missing_ents'][counter-1]] = $(sourceElem).val();
      $('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+$(sourceElem).val()+'</p></div>');
      counter = counter- 1;//This has to be not undefined
      question = 'Please provide the ' + obj['missing_ents'][counter]+ '.' ;
      $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');

    });//End of button click event



}//End of counter> index conditional
else{
  $('#InfoButton').click(function(){
    $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+doneMessage+'</p></div>');
    $("#InfoButton").hide();
    $("#clickButton").show();


  });//End of button click event



}
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Below this everything is different, this is before function separation
//Line below is just a check
$(destElem).text(JSON.stringify(obj['missing_ents']));

let counter = obj['missing_ents'].length-1;// this is 2 if intent is engagement: period, socialnetwork
$("#clickButton").hide();
$("#InfoButton").show();
let index = 0;
let question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
$('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
$('#InfoButton').click(function(){
  if (counter >= index){
    $('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+$(sourceElem).val()+'</p></div>');
    entity_store[obj['missing_ents'][index]] = $(sourceElem).val();
    index++;//This has to be not undefined
    question = 'Please provide the ' + obj['missing_ents'][index]+ '.' ;
    $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
  } else{
    $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+doneMessage+'</p></div>');
    $("#InfoButton").hide();
    $("#clickButton").show();
  };//end of if elseconditional
  //Stop this from going to undefined
  //So it means that it is not going to the else case inside button onclick
  //Figure this out



});//end of click function



}//End of else

}).fail(function() {
$(destElem).text("{{'Error: Could not contact server.' }}");
});
}
// put code here to clean webstorage variable on click of refresh button


$(document).ready(function () {
$("body").click(function(e) {
if($(e.target).attr('id') === "toTranslate") {
$("#InitialGreeting").show();
$("#loadingGif").show();
}

else {
$("#loadingGif").hide();
}
});
});

</script>
{% endblock %}
//-----------------------Almost there before Ajax return
{% extends 'bootstrap/base.html' %}



{% block title %}
    {% if title%}{{title}}  Fora{% else %}Welcome to Fora{% endif %}
{% endblock %}

{% block navbar %}
    <nav class="nnavbar navbar-light bg-light">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="{{ url_for('main.smart_post') }}"><img src="https://image-store.slidesharecdn.com/0f288636-1020-46c5-9831-0a13bf374d31-original.png" width="55" height="55" class="d-inline-block align-top" alt=""></a>

            </div>
            <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                <ul class="nav navbar-nav">
                    <li><a href="{{ url_for('main.index') }}"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Analytics</span></a></li>
                    <li><a href="{{ url_for('main.feed_manage') }}"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Calendar</span></a></li>

                <!--    <li><a href="{{ url_for('main.feed_manage') }}"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Manage Feeds</span></a></li> -->

                  <!--  <li><a href="#exampleModal2" data-toggle="modal" data-target="#exampleModal2"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Manage Feeds</span></a></li> -->
                <!--  <li><a href="{{ url_for('main.feed_manage') }}" data-toggle="modal" data-target="#exampleModal3"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Actual Manage Feeds</span></a></li> -->

                  <!--  <li><a href="{{ url_for('main.user', username=current_user.username) }}"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Dashboard</a></li> -->
                  <!--  <li><a href="{{ url_for('main.analytics') }}"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Analytics</span></a></li>-->
                <!--  <li><a href="#exampleModal3" data-toggle="modal" data-target="#exampleModal3"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Calendar</span></a></li> -->

                  <!--  <li><a href="{{ url_for('main.bokeh') }}">Bokeh</a></li>
                    <li><a href="{{ url_for('main.bokeh2') }}">Bokeh2</a></li>
                    <li><a href="{{ url_for('main.bokeh3') }}">Bokeh3</a></li>
                    <li><a href="{{ url_for('main.bokeh4') }}">Bokeh4</a></li>-->


                </ul>
                <ul class="nav navbar-nav navbar-right">
                    {% if current_user.is_anonymous %}
                    <li><a href="{{ url_for('auth.login') }}"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Login</span></a></li>
                    {% else %}
                    <li><a href="{{ url_for('auth.logout') }}"><span style = "border:1px blue solid; border-radius: 5px;padding: 10px;">Logout</span></a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
{% endblock %}

{% block content %}
    <div class="container" style= 'padding: 10px;'>
        {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
            <div class="alert alert-info" role="alert">{{ message }}</div>
            {% endfor %}
        {% endif %}
        {% endwith %}

        {# application content needs to be provided in the app_content block #}
        {% block app_content %}{% endblock %}
    </div>
{% endblock %}
{% block scripts %}
    {{ super() }}
    {{ moment.include_moment() }}

    <!-- This has all the good javascript functionality-->
    <script>
    let obj = [];
    let entity_store = {};
    let missing_entities = [];
    let counter = 0;
    let index = 0;
    let question = '';

    let image = new Image();
    image.src = "{{ url_for('static', filename='loading2.gif') }}"
    image.onload = function () {
      console.log('loading gif is ready to go!'); // remove this in production
    };
    $("#clickButton").click(function () {
      let text = $('#toTranslate').val();
      $('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+text+'</p></div>');
   });

    function translate(sourceElem, destElem) {
        $(destElem).html('<center><img src="{{ url_for('static', filename='loading2.gif') }}"></center>');

        $.post('/translate', {
            text: $(sourceElem).val()
        }).done(function(response) {
            obj = JSON.parse(response['text']);
            missing_entities = obj['missing_ents'];

            if (obj['missing_ents'].length === 0){
              //This should connect to the function giving the final solution
              $("#clickButton").hide();
              $("#refreshButton").show();
              let doneMessage  = 'Your result is displayed below. Please hit Refresh for more queries.'
              $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+doneMessage+'</p></div>');
              $(destElem).text("The engagement on Facebook from 10/11/2018 to 10/17/2018 was 70%.");
            }
            else {
              //Start of else///////////////////////////////////////////////////////////////////////////////////////
              //Below this everything is different
              //Line below is just a check
              counter = obj['missing_ents'].length;
              $(destElem).text(counter);
              question = 'Please provide the ' + obj['missing_ents'][counter-1]+ '.' ;
              $(destElem).text(' ');
              $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
              $("#clickButton").hide();
              $("#InfoButton").show();

            }//End of else

        }).fail(function() {
            $(destElem).text("{{'Error: Could not contact server.' }}");
        });
    }
    // put code here to clean webstorage variable on click of refresh button
    function infoHandle(sourceElem, destElem){
      if (counter != 0){
        $('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+$(sourceElem).val()+'</p></div>');
        entity_store[obj['missing_ents'][counter-1]] = $(sourceElem).val();
        counter = counter-1;
        question = 'Please provide the ' + obj['missing_ents'][counter-1]+ '.' ;
        $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
      } else{
        $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">Please hit Submit to get the result to your query from Fora</p></div>');
        $("#InfoButton").hide();
        $("#SubmitButton").show();
      }

    };//end of infoHandle

    $(document).ready(function () {
    $("body").click(function(e) {
      if($(e.target).attr('id') === "toTranslate") {
          $("#InitialGreeting").show();
          $("#loadingGif").show();
      }

      else {
          $("#loadingGif").hide();
      }
    });
  });

    </script>
{% endblock %}
//InfoHandle stuck
function infoHandle(sourceElem, destElem){
  if (counter > 1){
    $('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+$(sourceElem).val()+'</p></div>');
    entity_store[obj['missing_ents'][counter-1]] = $(sourceElem).val();
    counter = counter-1;
    question = 'Please provide the ' + obj['missing_ents'][counter-1]+ '.' ;
    $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">'+question+'</p></div>');
  } else if (counter == 1 ){
    $('#container').append('<div><p style = "display:inline-block;float: right; clear: both; border:1px LimeGreen solid; border-radius: 10px;padding: 5px;color: white; background-color:LimeGreen;">'+$(sourceElem).val()+'</p></div>');
    entity_store[obj['missing_ents'][counter-1]] = $(sourceElem).val();
    counter = counter-1;
  }else{
    $('#container').append('<div><p style = "display:inline-block; float: left; clear: both;border:1px DodgerBlue solid; border-radius: 10px;padding: 5px; color: white; background-color:DodgerBlue;">Please hit Submit to get the result to your query from Fora</p></div>');
    $(destElem).text(JSON.stringify(entity_store));
    $("#InfoButton").hide();
    $("#SubmitButton").show();
    //need to throw in a post function here to send data to the final calculation function \
    // This should be a composite function with the engagement and all the entities put together.
    // i.e. send_dic = {'intent': 'someEntity', entities: {'This': 'that','Another':'another_value'}}
  }

};//end of infoHandle
