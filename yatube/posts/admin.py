from django.contrib import admin

from .models import Group, Post, Comment


class PostAdmin(admin.ModelAdmin):

    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image')
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):

    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('description',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('title',)}


class CommentAdmin(admin.ModelAdmin):

    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_display = ('pk', 'text', 'pub_date', 'author', 'post')
    list_editable = ('post',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
