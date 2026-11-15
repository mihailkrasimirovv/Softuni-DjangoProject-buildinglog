from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect


class DeleteMessageMixin:
    """Used by the delete views.

    Shows a message after the object is deleted. If the database does not
    allow the deletion (protected records), shows an error instead of crashing.
    """

    success_message = "The record was deleted."
    protected_message = "The record cannot be deleted because other records depend on it."

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return redirect(self.object.get_absolute_url())
        messages.success(self.request, self.success_message)
        return response
