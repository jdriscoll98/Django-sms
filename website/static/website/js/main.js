var admin_email = "bobby@rdminnovation.com";
var system_administrator = "bobby@rdminnovation.com";
var csrftoken = getCookie('csrftoken');
var app_failing_notice = "The application is not working, please contact " + system_administrator + ".";

function app_failure() {
  alert(app_failing_notice);
}

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// -----------------------------------------------------------------------------
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
// -----------------------------------------------------------------------------
function setup_ajax() {
  // Setup CSRF for AJAX
  $.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
  });
}
// -----------------------------------------------------------------------------
function direct_to_href(element) {
  window.location.href = element.attr('href');
}
// -----------------------------------------------------------------------------
function set_active_menu_tab(tab_id) {
  $('.menu-item').each(function() {
    $(this).css({
      'background-color':'white',
      'color':'var(--secondary-color)'
    });
  });
  $('#' + tab_id).css({
    'background-color':'var(--secondary-color)',
    'color':'white'
  });
}
