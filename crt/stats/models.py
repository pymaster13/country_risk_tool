from django.db import models
from django.conf import settings

class Category(models.Model):

    name = models.CharField(max_length = 32,  blank = True, null = True)

    def __str__(self):
        return '{}'.format(self.name)

class Metric(models.Model):

    code = models.CharField(max_length = 32)
    name = models.CharField(max_length = 64)
    units =  models.CharField(max_length = 32)
    decription =  models.CharField(max_length = 256, blank = True, null = True)
    source =  models.CharField(max_length = 128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank = True, null = True)
    esg = models.CharField(max_length = 32, blank = True, null = True)
    sdg = models.CharField(max_length = 32, blank = True, null = True)
    descending = models.CharField(max_length = 1, blank = True, null = True)
    default = models.CharField(max_length = 1, blank = True, null = True)

    def __str__(self):
        return '{}'.format(self.name)

class Country(models.Model):

    iso = models.CharField(max_length = 3, blank = True, null = True, unique=True)
    name = models.CharField(max_length = 64, blank = True, null = True)

    def __str__(self):
        return '{}'.format(self.name)

class Link(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank = True, null = True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank = True, null = True)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, blank = True, null = True)
    value = models.FloatField(blank = True, null = True)

    def __str__(self):
        return '{}'.format(self.country, self.metric)

class Session(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    id_session = models.IntegerField()
    Capital = models.IntegerField(blank = True, null = True)
    Labour = models.IntegerField(blank = True, null = True)
    Productivity = models.IntegerField(blank = True, null = True)
    Fiscal = models.IntegerField(blank = True, null = True)
    Risks = models.IntegerField(blank = True, null = True)
    EcologicalFootprint = models.BooleanField(default = False)
    GHGIntensity = models.BooleanField(default = False)
    EnergyIntensity = models.BooleanField(default = False)
    WaterIntensity = models.BooleanField(default = False)
    ClimateCosts = models.BooleanField(default = False)
    InfraQuality = models.BooleanField(default = False)
    ForeignPop = models.BooleanField(default = False)
    EduAttainment = models.BooleanField(default = False)
    EaseBusiness = models.BooleanField(default = False)
    ICTDevelopment = models.BooleanField(default = False)
    KOFIndex = models.BooleanField(default = False)
    RegulatoryQuality = models.BooleanField(default = False)
    ClimateResilience = models.BooleanField(default = False)
    GlobalAdaptation = models.BooleanField(default = False)
    GovtEffectiveness = models.BooleanField(default = False)
    GDPPerCapita_min = models.CharField(max_length = 12, blank = True, null = True)
    GDPPerCapita_max = models.CharField(max_length = 12, blank = True, null = True)
    GDP_min = models.CharField(max_length = 12, blank = True, null = True)
    GDP_max = models.CharField(max_length = 12, blank = True, null = True)
    Number_countries = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return '{}'.format(self.id_session)

class Calc(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, blank = True, null = True)
    data = models.TextField(blank = True, null = True)

    def __str__(self):
        return '{}'.format(self.session)
