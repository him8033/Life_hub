from django.db import models
from django.utils.text import slugify

# Create your models here.


class Country(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=5, default="IN")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class State(models.Model):
    id = models.IntegerField(primary_key=True)  # LGD State Code
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # State or UT
    slug = models.SlugField(blank=True)


class District(models.Model):
    id = models.IntegerField(primary_key=True)  # LGD District Code
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)


class SubDistrict(models.Model):
    id = models.IntegerField(primary_key=True)  # LGD Sub-District Code
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)


class Village(models.Model):
    id = models.IntegerField(primary_key=True)  # LGD Village Code
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # Rural/Urban
    slug = models.SlugField(blank=True)


class Pincode(models.Model):
    pincode = models.CharField(max_length=10)
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name="pincodes")
