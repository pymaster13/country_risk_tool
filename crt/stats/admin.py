from django.contrib import admin
from stats.models import Category, Metric, Country, Link, Session, Calc

admin.site.register(Category)
admin.site.register(Country)
admin.site.register(Session)
admin.site.register(Calc)

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):

    list_display = ('id', 'code', 'name', 'units', 'decription', 'source',
    'category', 'esg', 'sdg', 'descending', 'default')

    def code(self):
        return self.code

    def name(self):
        return self.name

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):

    list_display = ('country', 'category', 'metric', 'value')

    def country(self):
        return self.country

    def metric(self):
        return self.metric

    def value(self):
        return self.value

