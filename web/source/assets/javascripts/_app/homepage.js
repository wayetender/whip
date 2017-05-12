//homepage.js

var APP = APP || {};

(function () {
  APP.Homepage = (function () {
    return {

      ui : null,

      init: function () {
        var _this = this;

        //cache elements
        this.ui = {
          $doc: $(window),
          $hero: $('#jumbotron'),
          $collapse: $('.navbar-collapse')
        }

        this.addEventListeners();

      },
      
      addEventListeners: function(){
        var _this = this;

        init_whip_vis([
          {x:40, y: 80, adapted: true}, 
          {x:140, y: 290, adapted: false},
          {x:440, y: 200, adapted: false},
          {x:740, y: 250, adapted: false},
          {x:940, y: 70, adapted: true},
          {x:972, y: 157, adapted: false},
          {x:980, y: 310, adapted: true},

          ], 
          1, document.getElementById('demoCanvas0'));

        init_whip_vis([
            {x:25, y: 50, adapted: true}, 
            {x:170, y:50, adapted: false}
          ], 
          1, document.getElementById('demoCanvas1'), {
            nodeColor: "#55318c",
            "lineOpacity": 0.5});

        init_whip_vis([
            {x:45, y: 40, adapted: true}, 
            {x:160, y:40, adapted: true},
            {x:102, y:100, adapted: false}
          ], 
          2, document.getElementById('demoCanvas2'), {
            nodeColor: "#55318c",
            "lineOpacity": 0.5});
        
        var tour = {
          id: "spec-full-service",
          steps: [
            {
              title: "Service Contracts",
              content: "The <code>service { ... }</code> block defines the contracts on a service interface.",
              target: "spec-full-service",
              placement: "right",
              onShow: function() {
                $('#spec-full-service').css('border', '1px dashed white');
              },
              onNext: function() {
                $('#spec-full-service').css('border', 'none');  
              }
            },
            {
              title: "Service Contracts",
              content: "This is the <code>Login</code> service",
              target: "spec-service-login",
              placement: "top"
            },
            {
              title: "Service Contracts",
              content: "... and this is the <code>User</code> service",
              target: "spec-service-user",
              placement: "top"
            },
            {
              title: "Service Operations",
              content: "Services contain operations. The <code>Login</code> service exposes a <code>register</code> operation which takes a username, email, and password.",
              target: "spec-register-op",
              placement: "bottom"
            },
            {
              title: "Operation Contracts",
              content: "Each operation can include preconditions and postconditions, defined by executable Python code. This precondition checks that the provided email is valid and the password is greater than 7 characters.",
              target: "spec-register-pre",
              placement: "bottom"
            },
            {
              title: "Operation Contracts",
              content: "Here, the <code>login</code> operation must return either <code>'success'</code> or <code>'failure'</code> in its status field.",
              target: "spec-login-post",
              placement: "top"
            },
            {
              title: "Higher-order contracts",
              content: "Additionally, operations may <em>identify</em> other services. In this example, the server at <code>userServiceURL</code> denotes a <code>User</code> service.",
              target: "spec-login-id",
              placement: "bottom"
            },
            {
              title: "Higher-order Contracts",
              content: "Services can be <em>indexed</em> by a parameter to an operation. Here the <code>authToken</code> is used as the index for the service. Indexes help ensure a service is properly used.",
              target: "spec-where-clause",
              placement: "bottom"
            },
          ]
        };

        $('#tour-btn').on('click', function () {
          hopscotch.startTour(tour);
        });

        if(APP.Utils.isMobile)
        return;

        _this.ui.$doc.scroll(function() {

          //if collapseable menu is open dont do parrallax. It looks wonky. Bootstrap conflict
          if( _this.ui.$collapse.hasClass('in'))
          return;

          var top = _this.ui.$doc.scrollTop(),
          speedAdj = (top*0.8),
          speedAdjOffset = speedAdj - top;

          _this.ui.$hero.css('webkitTransform', 'translate(0, '+ speedAdj +'px)');
          _this.ui.$hero.find('.container').css('webkitTransform', 'translate(0, '+  speedAdjOffset +'px)');
        })
      }
    }
  }());

}(jQuery, this));
