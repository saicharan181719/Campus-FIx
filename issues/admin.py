from django.contrib import admin

from .models import Category, Location, Issue, IssueUpdate


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )

    search_fields = (
        'name',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'block',
        'building',
        'room',
        'area',
    )

    search_fields = (
        'block',
        'building',
        'room',
        'area',
    )


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id',
        'title',
        'category',
        'location',
        'priority',
        'status',
        'reporter',
        'assigned_to',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'category',
        'assigned_to',
        'created_at',
    )

    search_fields = (
        'ticket_id',
        'title',
        'description',
        'reporter__username',
        'assigned_to__username',
    )

    readonly_fields = (
        'ticket_id',
        'created_at',
        'updated_at',
    )


@admin.register(IssueUpdate)
class IssueUpdateAdmin(admin.ModelAdmin):
    list_display = (
        'issue',
        'updated_by',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'issue__ticket_id',
        'comment',
        'updated_by__username',
    )

    readonly_fields = (
        'created_at',
    )