from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import AdoptionRequest


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "pet", "created_at", "phone", "short_reason", "status")
    list_filter = ("status", "pet__animal_type", "created_at")
    search_fields = ("user__username", "pet__name", "phone")
    list_select_related = ("user", "pet")
    actions = ["approve_requests", "reject_requests"]

    @admin.display(description="Reason")
    def short_reason(self, obj):
        return obj.reason if len(obj.reason) <= 60 else obj.reason[:57] + "..."

    def _change_status(self, request, queryset, new_status):
        done = 0
        for obj in queryset:
            if obj.status != AdoptionRequest.Status.PENDING:
                self.message_user(request, f"{obj}: only pending requests can be changed.", messages.WARNING)
                continue
            obj.status = new_status
            try:
                obj.full_clean()
            except ValidationError as e:
                self.message_user(request, f"{obj}: {'; '.join(e.messages)}", messages.ERROR)
                continue
            obj.save()
            done += 1
        self.message_user(request, f"{done} request(s) marked as {new_status}.", messages.SUCCESS)

    @admin.action(description="Approve selected pending requests")
    def approve_requests(self, request, queryset):
        self._change_status(request, queryset, AdoptionRequest.Status.APPROVED)

    @admin.action(description="Reject selected pending requests")
    def reject_requests(self, request, queryset):
        self._change_status(request, queryset, AdoptionRequest.Status.REJECTED)
