$(function() {
    $('.collapse').on('shown.bs.collapse', function() {
         $(this).parent().find(".glyphicon-chevron-left").removeClass("glyphicon-chevron-left").addClass("glyphicon-chevron-down");

    }).on('hidden.bs.collapse', function() {
	$(this).parent().find(".glyphicon-chevron-down").removeClass("glyphicon-chevron-down").addClass("glyphicon-chevron-left");
    });

    $('#vesselModal').bind("DOMSubtreeModified",function() {
	 alert('changed');

//       $('#id_predefined_conditions').on('click', function() {
//          alert('fff');
//       });
    });
});
function select_condition(input_id) {

     var input_value = $('#'+input_id).val();
     
     $.ajax({url: "/condition-predefined/"+input_value+"/", contentType: "application/json", dataType: "json", success: function(result) {
         $('#id_condition').val(result['0']['fields']['condition']);
     }});

     $('#'+input_id).val('');


}


