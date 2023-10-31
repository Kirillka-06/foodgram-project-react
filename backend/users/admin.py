from django.contrib import admin
from users.models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = (
        'first_name',
        'email'
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'follower'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
