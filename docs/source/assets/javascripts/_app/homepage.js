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
              title: "My Header",
              content: "This is the header of my page.",
              target: "spec-full-service",
              placement: "right"
            },
            {
              title: "My content",
              content: "Here is where I put my content.",
              target: "spec-service-test",
              placement: "bottom"
            }
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
