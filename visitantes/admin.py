from django.contrib import admin

from .models import Visit, Visitor


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'document', 'visitor_type', 'phone', 'email', 'created_at']
    search_fields = ['name', 'document', 'email']
    list_filter = ['visitor_type']
    ordering = ['-created_at']


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'visitor',
        'ticket_code',
        'check_in_at',
        'check_out_at',
        'companion_count',
        'is_active',
        'registered_by',
    ]
    list_filter = ['check_in_at']
    search_fields = ['visitor__name', 'ticket_code']
    date_hierarchy = 'check_in_at'
    readonly_fields = ['ticket_code', 'check_in_at', 'registered_by']

    @admin.display(boolean=True, description='Ativa?')
    def is_active(self, obj):
        return obj.is_active
