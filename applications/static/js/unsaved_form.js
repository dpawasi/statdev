var django_form_checks = { 
	var: {
	     'form_changed': null,
	},
        load: function() { 
	      $("form input[type=text]").change(function() { 
			      django_form_checks.var.form_changed = 'changed';
			      console.log('changed');
			      });

	      $("a").click(function(e) { 
                         var href= $(this).attr('href');
                         var reg = new RegExp(/^#.*$/);
                         if (href.match(reg)) {
			 } else {
		         	if (django_form_checks.var.form_changed == 'changed') {
				      var success = confirm('You have unsaved changes, please click the save button to avoid losing data,  are you sure you want to navigate away from this page?'); 
				      if (success == false) { 
					return false;
				      }
				}

			}
	      });	
			 


        },
};

window.onload = function () {
	django_form_checks.load();
}
