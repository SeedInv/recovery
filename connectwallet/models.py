# from django.db import models
# from django.contrib.auth.models import User

# # Model to store wallet assets (name and image)
# class WalletAsset(models.Model):
#     name = models.CharField(max_length=100)
#     wallet_image = models.ImageField(upload_to='wallet_images/', blank=True, null=True)

#     def __str__(self):
#         return self.name

# # Model to link a user to a wallet and store the wallet phrase
# class ConnectWallet(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user (changed from OneToOneField to ForeignKey)
#     wallet = models.ForeignKey(WalletAsset, on_delete=models.CASCADE)  # Link to WalletAsset
#     wallet_phrase = models.CharField(max_length=255, blank=True, null=True)  # Wallet phrase

#     def __str__(self):
#         return f"{self.user.username} - {self.wallet.name}"


from django.db import models
from django.contrib.auth.models import User

# Model to store wallet assets (name and image)
class WalletAsset(models.Model):
    name = models.CharField(max_length=100)
    wallet_image = models.ImageField(upload_to='wallet_images/', blank=True, null=True)

    def __str__(self):
        return self.name

# Model to link a user to a wallet and store the wallet phrase
class ConnectWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user (changed from OneToOneField to ForeignKey)
    wallet = models.ForeignKey(WalletAsset, on_delete=models.CASCADE)  # Link to WalletAsset
    wallet_phrase = models.CharField(max_length=255, blank=True, null=True)  # Wallet phrase

    def __str__(self):
        return f"{self.user.username} - {self.wallet.name}"
