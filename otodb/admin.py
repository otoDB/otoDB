from django.contrib import admin
from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from .models import (
    Category, Implication, Media, TagMain, Configuration, TaggedMedia
)

class TagMainAdmin(admin.ModelAdmin):
    readonly_fields = ('display_name',)
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }

class TaggedMediaAdmin(admin.ModelAdmin):
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }

class MediaAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.check_and_update_implications()

admin.site.register([
    Category,
    Implication,
    Configuration
])
admin.site.register(TagMain, TagMainAdmin)
admin.site.register(TaggedMedia, TaggedMediaAdmin)
admin.site.register(Media, MediaAdmin)
