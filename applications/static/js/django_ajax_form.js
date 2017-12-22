var django_ajax_form = {
      var: {
          form_html: ''

      },
      OpenForm: function(vessel_id) {
//        var crispy_form_load = $.get( "/applications/272/vessel/" ).responseText;
//	alert(crispy_form_load);
	
	$.ajax({
	    url: "/applications/283/vessel/",
	    async: false,
	    success: function(data) {
        	  django_ajax_form.var.form_html = data;
	    }
	});
        var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();

        var htmlvalue = "";
            htmlvalue += '<div id="vesselModal" class="modal fade" role="dialog">';
            htmlvalue += '<div class="modal-dialog modal-lg">';
            htmlvalue += '    <div class="modal-content">';
            htmlvalue += '      <div class="modal-header">';
            htmlvalue += '        <button type="button" class="close" data-dismiss="modal">&times;</button>';
            htmlvalue += '        <h4 class="modal-title">Vessel</h4>';
            htmlvalue += '      </div>';
            htmlvalue += '      <div class="modal-body">';
            htmlvalue += django_ajax_form.var.form_html;
            htmlvalue += '<form action="/applications-uploads/" method="post" enctype="multipart/form-data" id="upload_form">';
            htmlvalue += '<input type="hidden" name="csrfmiddlewaretoken" value="'+csrfmiddlewaretoken+'" />';
            htmlvalue += '</form>';
            htmlvalue += '<BR><BR>';

            htmlvalue += '<BR><BR>';
            htmlvalue += '<div class="modal-footer">';
            htmlvalue += '<BR><BR><button name="close" type="button" class="btn btn-primary" value="Close" class="close" data-dismiss="modal" value="Close">Close</button>';
            htmlvalue += '</div>';
            htmlvalue += '</div>';
            htmlvalue += '</div>';
            htmlvalue += '</div>';
            htmlvalue += '</div>';

            $('html').prepend(htmlvalue);
	    $('#vesselModal').modal({
        show: 'false'
 });


      },
      saveForm: function()  { 


var form_data = new FormData($('#id_form_create_vessel')[0]);
$.ajax({
url : '/applications/283/vessel/',
type: "POST",
data : form_data,
contentType: false,
cache: false,
processData:false,
xhr: function() {
//upload Progress
var xhr = $.ajaxSettings.xhr();
return xhr;
},
mimeType:"multipart/form-data"
}).done(function(res) { //
        django_form_checks.var.form_changed = 'changed';
        console.log('upload complete');
        var input_array =[];

        // $(form_id)[0].reset(); //reset form
        // $(result_output).html(res); //output response from server
        var obj = JSON.parse(res);
        var input_id_obj = $('#'+input_id+'_json').val();

        if (upload_type == 'multiple') {

        if (input_id_obj.length > 0) {
        	input_array = JSON.parse(input_id_obj);
        }

        input_array.push(obj);
        console.log(obj['doc_id']);
        console.log(input_id);

        } else {
                input_array = obj
        }

        $('#'+input_id+'_json').val(JSON.stringify(input_array));
        submit_btn.val("Upload").prop( "disabled", false); //enable submit button once ajax is done
        ajax_loader_django.showFiles(input_id,upload_type);
        $('#'+input_id+'__submit__files').val('');
}).fail(function(res) { //
        console.log('failed');

        $(result_output).append('<div class="error">Upload to Server Error</div>');
        $('#progress-bar-indicator').attr('class', 'progress-bar progress-bar-danger');

        var percent = '100';
        $(progress_bar_id +" .progress-bar").css("width", + percent +"%");
        $(progress_bar_id + " .status").text("0%");
        $(progress_bar_id + " .status-text").text("error");
        //submit_btn.val("Upload").prop( "disabled", false);
        });


}
}


//      }

//}
