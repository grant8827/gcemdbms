from django.contrib import admin
from .models import Transaction, Member, Tithing


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'category', 'amount', 'recorded_by']
    list_filter = ['type', 'category', 'date']
    search_fields = ['description', 'category']
    ordering = ['-date']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'member_since', 'is_active']
    list_filter = ['is_active', 'member_since']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']


@admin.register(Tithing)
class TithingAdmin(admin.ModelAdmin):
    list_display = ['member', 'date', 'amount', 'payment_method', 'recorded_by']
    list_filter = ['payment_method', 'date', 'is_active']
    search_fields = ['member__first_name', 'member__last_name', 'notes']
    ordering = ['-date']
    raw_id_fields = ['member']
