# -*- coding: utf-8 -*-
from django.contrib import admin

from app.admin_actions import verification_test_push_notifications, performance_test_push_notifications
from app.models import *


@admin.register(UserEmail)
class UserEmailAdmin(admin.ModelAdmin):
    list_filter = ['verified']
    readonly_fields = ['updated', 'created']


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_filter = ['verified']
    readonly_fields = ['updated', 'created']
    actions = [
        verification_test_push_notifications,
        performance_test_push_notifications,
    ]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_filter = ['city']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_filter = ['institution']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ['institution']


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_filter = ['location', 'location__institution', 'location__institution__city', 'category']


@admin.register(PerformanceNotification)
class PerformanceNotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(CategoryNotification)
class CategoryNotificationAdmin(admin.ModelAdmin):
    list_filter = ['verified']
    readonly_fields = ['updated', 'created']
