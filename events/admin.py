from django.contrib import admin
from . import models
# Register your models here.

filter_list = [ (var[0],var[2]) for var in models.condition_list ]

class FilledFilter(admin.SimpleListFilter):
    title = 'Заполненность'
    parameter_name = 'filled_filter'

    def lookups(self, request, model_admin):
        return filter_list

    def queryset(self, request, queryset):
        filter_value = self.value()
        query_cond=[]
        for var in filter_list:
            if var[0] == filter_value:
                for query in queryset:
                    if var[1] in query.display_places_left(): query_cond.append(query.id)
        if len(query_cond) > 0: return queryset.filter(id__in = query_cond)
        return queryset

class AutoInstanceInline(admin.TabularInline):
    model = models.Review
    extra = 0
    readonly_fields = ['user', 'text', 'rate', 'created', 'updated', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'display_enroll_count', 'display_places_left']
    list_display = ['id', 'title', 'category', 'date_start', 'is_private', 'participants_number', 'display_enroll_count', 'display_places_left', ]
    list_select_related = ['category', ]
    ordering = ['date_start', ]
    search_fields = ['title',]
    list_filter = [FilledFilter, 'category', 'features', ]
    filter_horizontal = ['features',]
    fields = ['title', 'description', 'date_start', 'participants_number', 'is_private', 'category','features', 'display_enroll_count', 'display_places_left', ]
    inlines = [AutoInstanceInline]

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['id', ]
    list_display = ['id', 'title', 'display_event_count', ]
    list_display_links = ['id', 'title', ]


@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', ]
    list_display_links = ['id', 'title', ]

@admin.register(models.Enroll)
class EnrollAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'created', ]
    list_display_links = ['id', 'user', 'event', ]
    list_select_related = ['event', 'user', ]


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'created', 'updated', ]
    list_display = ['id', 'user', 'event', 'rate', 'created', 'updated', ]
    list_display_links = ['id', 'user', 'event', ]
    list_filter = ['created', 'event', ]
    list_select_related = ['event', 'user', ]
    fields = ['created', 'updated', 'id']