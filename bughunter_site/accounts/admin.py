from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VerificationToken, BugHunterJob


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'is_verified')}),
    )


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expires_at')
    list_filter = ('expires_at',)
    search_fields = ('user__username', 'user__email')


@admin.register(BugHunterJob)
class BugHunterJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'github_url')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'github_url')
    readonly_fields = ('created_at',)