from django import forms


class DateInput(forms.DateInput):
    """Date picker (<input type="date">). The browser needs the value as YYYY-MM-DD."""

    input_type = "date"

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, format="%Y-%m-%d")


class BootstrapFormMixin:
    """Adds the Bootstrap CSS classes to the fields of a form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxSelectMultiple):
                # the list of checkboxes is styled in buildlog.css
                continue
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"


class ReadOnlyFieldsMixin:
    """Disables the fields listed in read_only_fields.

    A disabled field is shown, but the value sent by the browser is ignored.
    """

    read_only_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.read_only_fields:
            self.fields[field_name].disabled = True
