from django.contrib import admin

from .models import FixedCostEntry


@admin.register(FixedCostEntry)
class FixedCostEntryAdmin(admin.ModelAdmin):
    list_display = [
        'category',
        'description',
        'value',
        'due_date',
        'paid_at',
        'status',
        'created_by',
    ]
    list_filter = ['category', 'status', 'due_date']
    search_fields = ['description']
    date_hierarchy = 'due_date'
    readonly_fields = ['paid_at', 'created_at', 'updated_at', 'created_by', 'updated_by']