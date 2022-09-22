(function ($) {
    $(document).on(
        "click",
        "#submit",
        function (eventObject) {
            // Form submission logic
            var domForm = $('form').get(0);
            if (domForm.reportValidity()) {    // validate
                if ($("form :checked").length ) {
                    // overwrite selected
                    // open modal
                    $('#overwriteModal').modal('show');
                } else {
                    // no overwrite
                    // submit
                    domForm.requestSubmit();
                }
            }
        }
    )

    $(document).on(
        "click",
        "#confirm",
        function (eventObject) {
            // User confirm
            // Submit form
            $('form').get(0).requestSubmit();
        }
    )
})(django.jQuery)