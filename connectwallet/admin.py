# admin.py
from django.contrib import admin
from .models import WalletAsset, ConnectWallet

class WalletAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'wallet_image']
    search_fields = ['name']

class ConnectWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'wallet', 'wallet_phrase']
    search_fields = ['user__username', 'wallet__name']
    list_filter = ['user']

admin.site.register(WalletAsset, WalletAssetAdmin)
admin.site.register(ConnectWallet, ConnectWalletAdmin)

