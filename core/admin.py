from django.contrib import admin
from .models import Video, Tag, TranscriptSegment

admin.site.register(Video)
admin.site.register(Tag)
admin.site.register(TranscriptSegment)


# Register your models here.
