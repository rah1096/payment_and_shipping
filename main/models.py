from django.db import models

# Create your models here.
class Item(models.Model):
    item_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=True, unique=True)
    description = models.TextField()
    manufacturer = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)

    def __unicode__(self):
        return self.title


