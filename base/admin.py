from django.contrib import admin

# Register your models here.

from .models import Room, Topic, Message, User, CodeSnippet, Document

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(CodeSnippet)
admin.site.register(Document)
# admin.site.register(Note)