from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.shortcuts import render
from django.views.generic import FormView
from django.shortcuts import redirect
from django.http import HttpResponse

import csv, json, pygal
from collections import OrderedDict

from .forms import UploadFileForm
from .models import *


def str_to_json(id_session):
    data_session = Calc.objects.get(session = Session.objects.get(id_session = id_session))
    data = data_session.data
    data1 = data.replace('{\'','{\"')
    data2 = data1.replace('\':','\":')
    data3 = data2.replace(' \'',' \"')
    data4 = data3.replace('\',','\",')
    data_json = data4.replace('\'}','{\"}')
    context = json.loads(data_json)
    return context

class UploadView(UserPassesTestMixin, FormView):
    template_name = "upload.html"
    form_class = UploadFileForm
    success_url = "/"
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.process_data()
        return super().form_valid(form)

def TableCountries(request):
    categories_set = Category.objects.exclude(name = "Valuation")
    metrics_set = Metric.objects.all()
    count_category_dict = {}
    coverage = {}
    for category in categories_set:
        i = 0
        for metric in metrics_set:
            if category == metric.category:
                i += 1
        count_category_dict.update({str(category) : str(i)})

    countrys = Country.objects.all()
    country_len = len(countrys)

    for metr in metrics_set:
        links = len(Link.objects.filter(metric = metr))
        try:
            lens = int(links / country_len * 100)
        except:
            lens = 0
        coverage.update({metr.name : str(lens)})

    context = {"metrics": metrics_set, "categories": categories_set, 
        "count" : count_category_dict, "coverage" : coverage}

    return context

@login_required(login_url='/')
def TableView(request):

    if request.method == "POST":
        data = request.POST

        if "number_countries" in data:
            min_GDP_cap = data["min_GDP_cap"]
            max_GDP_cap = data["max_GDP_cap"]
            min_GDP = data["min_GDP"]
            max_GDP = data["max_GDP"]
            countries = Country.objects.all()
            metrics = Metric.objects.all()
            links = Link.objects.all()
            max_list_GDP_cap = Link.objects.filter(
                metric = metrics.get(name = "GDP per capita")).aggregate(Max("value"))
            max_list_GDP = Link.objects.filter(
                metric = metrics.get(name = "Gross domestic product")).aggregate(Max("value"))
            min_list_GDP_cap = Link.objects.filter(
                metric = metrics.get(name = "GDP per capita")).aggregate(Min("value"))
            min_list_GDP = Link.objects.filter(
                metric = metrics.get(name = "Gross domestic product")).aggregate(Min("value"))

            if min_GDP_cap == "":
                min_GDP_cap = 0
            if max_GDP_cap == "":
                max_GDP_cap = max_list_GDP_cap["value__max"] + 1
            if min_GDP == "":
                min_GDP = 0
            if max_GDP == "":
                max_GDP = max_list_GDP["value__max"] + 1

            number_country = 0
            right_country = []
            for country in countries:
                link = Link.objects.filter(country = country)
                x = 0
                for l in link:
                    if l.metric == metrics.get(name = "Gross domestic product") and float(min_GDP) < l.value < float(max_GDP):
                        x += 1
                    if l.metric == metrics.get(name = "GDP per capita") and float(min_GDP_cap) < l.value < float(max_GDP_cap):
                        x += 1
                if x == 2:
                    number_country += 1
                    right_country.append(country)

            context = {"Number_countries": number_country, "countries": right_country}
            context.update(TableCountries(data))
            context.update({"GDP" : data})
            count_session = Session.objects.filter(user = request.user)
            context.update({"next_id_session": len(count_session)})
            
            return render(request, "../templates/table.html", context)

        elif "data_save_server" in data:
            """session"""
            all_countries = len(Country.objects.all())
            session_count = len(Session.objects.filter(user = request.user))
            session = Session(user = request.user, id_session = session_count + 1)
            fields_model = session._meta.get_fields()
            metrics_checked = []

            for key, value in data.items():
                if value == "on":
                    metrics_checked.append(key)
            for metric in metrics_checked:
                setattr(session, metric, True)
            session.save()

            weight_sum = int(int(data["Capital"]) + int(data["Labour"]) + int(data["Productivity"]) +
                int(data["Fiscal"]) + int(data["Risks"]))

            if weight_sum == 100:
                session.Capital = data["Capital"]
                session.Labour = data["Labour"]
                session.Productivity = data["Productivity"]
                session.Fiscal = data["Fiscal"]
                session.Risks = data["Risks"]
            else:
                koef = 100 / weight_sum
                session.Capital = int(int(data["Capital"]) * koef)
                session.Labour = int(int(data["Labour"]) * koef)
                session.Productivity = int(int(data["Productivity"]) * koef)
                session.Fiscal = int(int(data["Fiscal"]) * koef)
                session.Risks = int(int(data["Risks"]) * koef)

            session.GDPPerCapita_min = data["min_GDP_cap"]
            session.GDPPerCapita_max = data["max_GDP_cap"]
            session.GDP_min = data["min_GDP"]
            session.GDP_max = data["max_GDP"]
            session.save()
            id_session = session.id_session

            """ CALCULATIONS """
            user_sessions = Session.objects.get(user = request.user, id_session = id_session)
            min_GDP_cap = user_sessions.GDPPerCapita_min
            max_GDP_cap = user_sessions.GDPPerCapita_max
            min_GDP = user_sessions.GDP_min
            max_GDP = user_sessions.GDP_max
            countries = Country.objects.all()
            metrics = Metric.objects.all()
            links = Link.objects.all()
            max_list_GDP_cap = Link.objects.filter(metric = metrics.get(name = "GDP per capita")).aggregate(Max("value"))
            max_list_GDP = Link.objects.filter(metric = metrics.get(name = "Gross domestic product")).aggregate(Max("value"))
            min_list_GDP_cap = Link.objects.filter(metric = metrics.get(name = "GDP per capita")).aggregate(Min("value"))
            min_list_GDP = Link.objects.filter(metric = metrics.get(name = "Gross domestic product")).aggregate(Min("value"))

            if min_GDP_cap == "":
                min_GDP_cap = 0
            if max_GDP_cap == "":
                max_GDP_cap = max_list_GDP_cap["value__max"] + 1
            if min_GDP == "":
                min_GDP = 0
            if max_GDP == "":
                max_GDP = max_list_GDP["value__max"] + 1
            number_country = 0
            right_country = []
            for country in countries:
                link = Link.objects.filter(country = country)
                x = 0
                for l in link:
                    if l.metric == metrics.get(name = "Gross domestic product") and  float(min_GDP) < l.value < float(max_GDP):
                        x += 1
                    if l.metric == metrics.get(name = "GDP per capita") and float(min_GDP_cap) < l.value < float(max_GDP_cap):
                        x += 1
                if x == 2:
                    number_country += 1
                    right_country.append(country.iso)

            session.Number_countries = number_country
            session.save()

            country_link = Link.objects.filter(country__in = Country.objects.filter(iso__in = right_country))
            metrics_need = Metric.objects.exclude(code__in = ["GDPPerCapita", "GDP"])

            rezult = {}
            list_category = ["Capital", "Labour", "Productivity", "Fiscal capacity", "Risks"]
            list_reverse_metric = ["EcologicalFootprint", "GHGIntensity", 
                "EnergyIntensity", "WaterIntensity", "ClimateCosts"]
            list_environment = ["EcologicalFootprint", "GHGIntensity", 
                "EnergyIntensity", "WaterIntensity", "ClimateCosts", "ClimateResilience"]
            list_social = ["ForeignPop", "EduAttainment", "ICTDevelopment", "KOFIndex"]
            list_governance = ["InfraQuality", "EaseBusiness", "RegulatoryQuality", 
                "GlobalAdaptation", "GovtEffectiveness"]
            list_people = ["ForeignPop", "ICTDevelopment"]
            list_planet = ["EcologicalFootprint", "GHGIntensity", "EnergyIntensity", 
                "WaterIntensity", "ClimateCosts", "ClimateResilience"]
            list_prosperity = ["InfraQuality", "EduAttainment", "GlobalAdaptation"]
            list_peace = ["EaseBusiness", "KOFIndex"]
            list_partnership = ["RegulatoryQuality", "GovtEffectiveness"]

            dict_category = {"Capital": [], "Labour": [], "Productivity": [],
                 "Fiscal capacity": [], "Risks": []}
            dict_mark = {"Environment": [], "Social": [], "Governance": [], 
                "People": [], "Planet": [], "Prosperity": [], "Peace": [], "Partnership": []}

            for country in right_country:
                rezult.update({country : {}})
                rezult[country].update({"avg" : {}, "position": {}, "mark_avg" : {},
                     "mark_rang" : {}, "country": Country.objects.get(iso = country).name})
                for category in list_category:
                    rezult[country].update({category : {}})
                for metric in metrics_need:
                    if metric in list_reverse_metric:
                        try:
                            country_metric_value = Link.objects.get(country = Country.objects.get(iso = str(country)),
                                 metric = Metric.objects.get(name = str(metric)))
                            link_category = country_metric_value.category
                            above = len(country_link.filter(metric = metric).filter(value__gt=country_metric_value.value))
                            below = len(country_link.filter(metric = metric).filter(value__lt=country_metric_value.value))
                            sred = 100 - (int(below) / (int(above) + int(below)) * 100)
                            try:
                                rezult[country][str(link_category)].update({metric.code : int(sred)})
                            except:
                                continue
                        except Link.DoesNotExist:
                            continue
                    else:
                        try:
                            country_metric_value = Link.objects.get(country = Country.objects.get(iso = str(country)),
                                 metric = Metric.objects.get(name = str(metric)))
                            link_category = country_metric_value.category
                            above = len(country_link.filter(metric = metric).filter(value__gt=country_metric_value.value))
                            below = len(country_link.filter(metric = metric).filter(value__lt=country_metric_value.value))
                            sred = int(below) / (int(above) + int(below)) * 100
                            try:
                                rezult[country][str(link_category)].update({metric.code : int(sred)})
                            except:
                                continue
                        except:
                            continue

                for category in list_category:
                    count_category = count_environment = count_social = count_governance = count_people = count_prosperity = count_peace = count_partnership = 0
                    avg_category = avg_environment = avg_social = avg_governance = avg_people = avg_prosperity = avg_peace = avg_partnership = 0
                    for metr, val in rezult[country][category].items():
                        count_category += 1
                        avg_category += val
                        if metr in list_environment:
                            count_environment += 1
                            avg_environment += val
                        if metr in list_social:
                            count_social += 1
                            avg_social += val
                        if metr in list_governance:
                            count_governance += 1
                            avg_governance += val
                        if metr in list_people:
                            count_people += 1
                            avg_people += val
                        if metr in list_prosperity:
                            count_prosperity += 1
                            avg_prosperity += val
                        if metr in list_peace:
                            count_peace += 1
                            avg_peace += val
                        if metr in list_partnership:
                            count_partnership += 1
                            avg_partnership += val
                    
                    if count_category != 0:
                        rezult[country]["avg"].update({category : int(avg_category / count_category)})
                        dict_category[category].append(int(avg_category / count_category))
                    
                    if count_environment != 0:
                        rezult[country]["mark_avg"].update({"Environment" : int(avg_environment / count_environment)})
                        rezult[country]["mark_avg"].update({"Planet" : int(avg_environment / count_environment)})
                        dict_mark["Environment"].append(int(avg_environment / count_environment))
                        dict_mark["Planet"].append(int(avg_environment / count_environment))
                    if count_social != 0:
                        rezult[country]["mark_avg"].update({"Social" : int(avg_social / count_social)})
                        dict_mark["Social"].append(int(avg_social / count_social))
                    if count_governance != 0:
                        rezult[country]["mark_avg"].update({"Governance" : int(avg_governance / count_governance)})
                        dict_mark["Governance"].append(int(avg_governance / count_governance))
                    if count_people != 0:
                        rezult[country]["mark_avg"].update({"People" : int(avg_people / count_people)})
                        dict_mark["People"].append(int(avg_people / count_people))
                    if count_prosperity != 0:
                        rezult[country]["mark_avg"].update({"Prosperity" : int(avg_prosperity / count_prosperity)})
                        dict_mark["Prosperity"].append(int(avg_prosperity / count_prosperity))
                    if count_peace != 0:
                        rezult[country]["mark_avg"].update({"Peace" : int(avg_peace / count_peace)})
                        dict_mark["Peace"].append(int(avg_peace / count_peace))
                    if count_partnership != 0:
                        rezult[country]["mark_avg"].update({"Partnership" : int(avg_partnership / count_partnership)})
                        dict_mark["Partnership"].append(int(avg_partnership / count_partnership))
            
            list_mark = ["Environment", "Social", "Governance", "People", "Planet", "Prosperity", "Peace", "Partnership"]
            
            for cat in list_category:
                dict_category[cat].sort()
            for mark in list_mark:
                dict_mark[mark].sort()
            for country in rezult:
                for category in list_category:
                    all_avg = len(dict_category[category])
                    try:
                        place = dict_category[category].index(rezult[country]["avg"][category]) + 1
                    except:
                        continue
                    sred = int(place / all_avg * 100)
                    rezult[country]["position"].update({category : sred})
                for mark in list_mark:
                    all_avg = len(dict_mark[mark])
                    try:
                        place = dict_mark[mark].index(rezult[country]["mark_avg"][mark]) + 1
                    except:
                        continue
                    sred = int(place / all_avg * 100)
                    rezult[country]["mark_rang"].update({mark : sred})
            
            """Weighted average"""
            Capital_weight = user_sessions.Capital
            Labour_weight = user_sessions.Labour
            Productivity_weight = user_sessions.Productivity
            Fiscal_weight = user_sessions.Fiscal
            Risks_weight = user_sessions.Risks
            
            country_list_average = []
            for country in rezult:
                country_average = 0
                for category in list_category:
                    if category == "Fiscal capacity":
                        try:
                            country_average += rezult[country]["position"][category] * getattr(user_sessions, "Fiscal") / 100
                        except:
                            continue
                    else:
                        try:
                            country_average += rezult[country]["position"][category] * getattr(user_sessions, category) / 100
                        except:
                            continue
                rezult[country].update({"Weighted_average" : int(country_average)})
                country_list_average.append(int(country_average))
            
            """ Overall ranking """
            country_list_average.sort()
            for country in rezult:
                all_avg = len(country_list_average)
                try:
                    place = country_list_average.index(rezult[country]["Weighted_average"]) + 1
                except:
                    continue
                sred = int(place / all_avg * 100)
                rezult[country].update({"Overall_ranking" : sred})

            """Predictions"""
            countries = right_country
            gdp_per_capita = []
            overall = []
            x_avg = 0
            y_avg = 0
            for country in countries:
                over = rezult[country]["Overall_ranking"]
                overall.append(over)
                gdp = Link.objects.get(country = Country.objects.get(iso = str(country)),
                     metric = Metric.objects.get(code = 'GDPPerCapita'))
                gdp_per_capita.append(gdp.value)
                x_avg += gdp.value
                y_avg += over
            x_avg = x_avg/len(gdp_per_capita)
            y_avg = y_avg/len(overall)

            b1 = 0
            b2 = 0

            for i in range(0,len(countries)):
                b1 += (abs(gdp_per_capita[i] - x_avg) * abs(overall[i] - y_avg))
                b2 += (abs(gdp_per_capita[i] - x_avg) * abs(gdp_per_capita[i] - x_avg))

            b = b1/b2
            a = y_avg - b*x_avg

            for country in countries:
                x = Link.objects.get(country = Country.objects.get(iso = str(country)),
                    metric = Metric.objects.get(code = 'GDPPerCapita'))
                y = a + b*x.value
                rezult[country].update({"Estimated_ranking" : int(y)})

            context = {"data" : {}}
            d = OrderedDict(sorted(rezult.items(), key=lambda x: x[1]["Overall_ranking"], reverse=True))
            context["data"].update(d)
            count_session = Session.objects.filter(user = request.user)
            context.update({"now_id_session": len(count_session)})
            
            Calculations = Calc(session = Session.objects.get(user = request.user, id_session = id_session), data = context)
            Calculations.save()
            
            count_session = Session.objects.filter(user = request.user)
            url_session = str(len(count_session) ) + "/"
            response = redirect(url_session)
            
            return response

    categories_set = Category.objects.exclude(name = "Valuation")
    metrics_set = Metric.objects.all()
    count_category_dict = {}
    coverage = {}
    for category in categories_set:
        i = 0
        for metric in metrics_set:
            if category == metric.category:
                i += 1
        count_category_dict.update({str(category) : str(i)})
    
    countrys = Country.objects.all()
    country_len = len(countrys)
    for metr in metrics_set:
        links = len(Link.objects.filter(metric = metr))
        try:
            lens = int(links / country_len * 100)
        except:
            lens = 0
        coverage.update({metr.name : str(lens)})
    
    """Sessions"""
    user_sessions = Session.objects.filter(user = request.user)
    user_sessions_list = {"sessions" : {}}
    for session in user_sessions:
        user_sessions_list["sessions"].update({str(session.id_session) : str(session.id_session) + ") " + 
            str(session.Number_countries) + " country(ies), weights: " + str(session.Capital) + ", " +
            str(session.Labour) + ", " +str(session.Productivity) + ", " +str(session.Fiscal) + ", " +str(session.Risks) +'.'})
    context = {"metrics": metrics_set, "categories": categories_set, "count" : count_category_dict, "coverage" : coverage}
    context.update(user_sessions_list)
    context.update({"next_id_session": int(len(user_sessions_list["sessions"]) + 2)})
    return render(request, "../templates/table.html", context)


@login_required(login_url='/')
def TableSession(request, id_session):
    if request.POST:
        if "save_csv" in request.POST:
            data = str_to_json(id_session)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
            writer = csv.writer(response)
            writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
            writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
            with open('F://dir/', "w", newline='') as csv_file:
                csv.close()

    categories_set = Category.objects.exclude(name = "Valuation")
    session_id = Session.objects.get(user = request.user, id_session = id_session)
    metrics_set = Metric.objects.all()
    count_category_dict = {}
    coverage = {}

    for category in categories_set:
        i = 0
        for metric in metrics_set:
            if category == metric.category:
                i += 1
        count_category_dict.update({str(category) : str(i)})
    countrys = Country.objects.all()
    country_len = len(countrys)

    for metr in metrics_set:
        links = len(Link.objects.filter(metric = metr))
        try:
            lens = int(links / country_len * 100)
        except:
            lens = 0
        coverage.update({metr.name : str(lens)})

    """Sessions list"""
    user_sessions = Session.objects.filter(user = request.user)
    user_sessions_list = {"sessions" : {}}
    for session in user_sessions:
        user_sessions_list["sessions"].update({str(session.id_session) : str(session.id_session) + ") " + 
            str(session.Number_countries) + " county(s), weight:" + str(session.Capital) + ", " +
            str(session.Labour) + ", " +str(session.Productivity) + ", " +str(session.Fiscal) + ", " +str(session.Risks)})
    context = {"metrics": metrics_set, "categories": categories_set, "count" : count_category_dict, "coverage" : coverage}
    context.update(user_sessions_list)

    """Sessions data"""
    session_data = {"weights": {}, "checked": {}}
    session_data["weights"].update({"Capital" : session_id.Capital})
    session_data["weights"].update({"Labour" : session_id.Labour})
    session_data["weights"].update({"Productivity" : session_id.Productivity})
    session_data["weights"].update({"Fiscal capacity" : session_id.Fiscal})
    session_data["weights"].update({"Risks" : session_id.Risks})

    session_data["checked"].update({"EcologicalFootprint" : session_id.EcologicalFootprint})
    session_data["checked"].update({"GHGIntensity" : session_id.GHGIntensity})
    session_data["checked"].update({"EnergyIntensity" : session_id.EnergyIntensity})
    session_data["checked"].update({"WaterIntensity" : session_id.WaterIntensity})
    session_data["checked"].update({"ClimateCosts" : session_id.ClimateCosts})
    session_data["checked"].update({"InfraQuality" : session_id.InfraQuality})
    session_data["checked"].update({"ForeignPop" : session_id.ForeignPop})
    session_data["checked"].update({"EduAttainment" : session_id.EduAttainment})
    session_data["checked"].update({"EaseBusiness" : session_id.EaseBusiness})
    session_data["checked"].update({"ICTDevelopment" : session_id.ICTDevelopment})
    session_data["checked"].update({"KOFIndex" : session_id.KOFIndex})
    session_data["checked"].update({"RegulatoryQuality" : session_id.RegulatoryQuality})
    session_data["checked"].update({"ClimateResilience" : session_id.ClimateResilience})
    session_data["checked"].update({"GlobalAdaptation" : session_id.GlobalAdaptation})
    session_data["checked"].update({"GovtEffectiveness" : session_id.GovtEffectiveness})

    session_data.update({"min_GDP_cap" : session_id.GDPPerCapita_min})
    session_data.update({"max_GDP_cap" : session_id.GDPPerCapita_max})
    session_data.update({"min_GDP" : session_id.GDP_min})
    session_data.update({"max_GDP" : session_id.GDP_max})
    session_data.update({"Number_countries" : session_id.Number_countries})

    countries = str_to_json(id_session)
    context.update(countries)
    context.update(session_data)
    context.update({'now_id_session' : id_session})
    return render(request, "../templates/table_session.html", context)

@login_required(login_url='/')
def RankingAll(request, id_session):
    context = str_to_json(id_session)
    return render(request, "../templates/rank_all.html", context)

@login_required(login_url='/')
def RankingCategory(request, id_session):
    context = str_to_json(id_session)
    return render(request, "../templates/rank_category.html", context)

@login_required(login_url='/')
def RankingESG(request, id_session):
    context = str_to_json(id_session)
    return render(request, "../templates/rank_ESG.html", context)

@login_required(login_url='/')
def RankingSDG(request, id_session):
    context = str_to_json(id_session)
    return render(request, "../templates/rank_SDG.html", context)

@login_required(login_url='/')
def CountryInfo(request, id_session, iso):

    data_json = str_to_json(id_session)
    data_country = {'data':{iso : {}}, 'countries' : {}}
    gdp = Link.objects.get(country = Country.objects.get(iso = str(iso)), metric = Metric.objects.get(code = 'GDPPerCapita'))
    data_country['data'][iso].update(data_json['data'][iso])

    for key, value in data_country['data'][iso].items():
        if key == 'Capital' or key == 'Labour' or key == 'Productivity' or key == 'Fiscal' or key == 'Risks':
            for metr_name, metr_data in value.items() :
                category_value = data_country['data'][iso][key][metr_name]
                if type(category_value) == type(1):
                    del data_country['data'][iso][key][metr_name]
                    data_country['data'][iso][key].update({metr_name : {}})
                    metr = Metric.objects.get(code = metr_name)
                    link = Link.objects.get(country = Country.objects.get(iso = iso), metric = metr)
                    data_country['data'][iso][key][metr_name].update({'code' : metr_name, 'unit' : metr.units,
                        'value' : "%.3f" % link.value, 'rank' : category_value, 'name' : metr.name})

    value = "%.3f" % gdp.value
    data_country['data'][iso].update({'GDPPerCapita': value})
    vs = abs(data_country['data'][iso]['Overall_ranking'] - data_country['data'][iso]['Estimated_ranking'])
    data_country['data'][iso].update({'vs': vs})
    for key, value in data_json['data'].items():
        data_country['countries'].update({key : value['country']})
    data_country.update({'now_id_session' : data_json['now_id_session']})

    return render(request, "../templates/country_info.html", data_country)

def CountryComparison(request, id_session):
    if request.method == "POST":
        data = request.POST
        categories_set = Category.objects.exclude(name = "Valuation")
        metrics_set = Metric.objects.all()
        count_category_dict = {}
        coverage = {}
        data_json = str_to_json(id_session)

        for key, value in data_json['data'].items():
            for category in categories_set:
                for metric in Metric.objects.filter(category = category):
                    try:
                        a = value[category.name]
                        try:
                            b = value[category.name][metric.code]
                        except:
                            data_json['data'][key][category.name].update({metric.code : '-'})
                            pass
                    except:
                        pass

        for key, value in data_json['data'][data['profile']].items():
            if key == 'Capital' or key == 'Labour' or key == 'Productivity' or key == 'Fiscal' or key == 'Risks':
                for metr_name, metr_data in value.items() :
                    category_value = data_json['data'][data['profile']][key][metr_name]
                    if type(category_value) == type(1) or type(category_value) == type('-'):
                        del data_json['data'][data['profile']][key][metr_name]
                        data_json['data'][data['profile']][key].update({metr_name : {}})
                        metr = Metric.objects.get(code = metr_name)
                        data_json['data'][data['profile']][key][metr_name].update({'code' : metr_name,
                            'unit' : metr.units, 'rank' : category_value, 'name' : metr.name})

        for key, value in data_json['data'][data['comparison']].items():
            if key == 'Capital' or key == 'Labour' or key == 'Productivity' or key == 'Fiscal' or key == 'Risks':
                for metr_name, metr_data in value.items() :
                    category_value = data_json['data'][data['comparison']][key][metr_name]
                    if type(category_value) == type(1) or type(category_value) == type('-'):
                        del data_json['data'][data['comparison']][key][metr_name]
                        data_json['data'][data['comparison']][key].update({metr_name : {}})
                        metr = Metric.objects.get(code = metr_name)
                        data_json['data'][data['comparison']][key][metr_name].update({'code' : metr_name,
                            'unit' : metr.units, 'rank' : category_value, 'name' : metr.name})
        
        data_country = {'data' : {}, 'countries' : {}}
        data_country['data'].update({'first':{data['profile'] : {}}})
        data_country['data'].update({'second':{data['comparison'] : {}}})
        gdp_profile = Link.objects.get(country = Country.objects.get(iso = data['profile']), metric = Metric.objects.get(code = 'GDPPerCapita'))
        gdp_comparison = Link.objects.get(country = Country.objects.get(iso = data['comparison']), metric = Metric.objects.get(code = 'GDPPerCapita'))
        data_country['data']['first'][data['profile']].update(data_json['data'][data['profile']])
        data_country['data']['second'][data['comparison']].update(data_json['data'][data['comparison']])
        value_profile = "%.3f" % gdp_profile.value
        value_comparison = "%.3f" % gdp_comparison.value
        data_country['data']['first'][data['profile']].update({'GDPPerCapita': value_profile})
        data_country['data']['second'][data['comparison']].update({'GDPPerCapita': value_comparison})

        vs_profile = abs(data_country['data']['first'][data['profile']]['Overall_ranking'] -
            data_country['data']['first'][data['profile']]['Estimated_ranking'])
        vs_comparison = abs(data_country['data']['second'][data['comparison']]['Overall_ranking'] -
            data_country['data']['second'][data['comparison']]['Estimated_ranking'])
        
        data_country['data']['first'][data['profile']].update({'vs': vs_profile})
        data_country['data']['second'][data['comparison']].update({'vs': vs_comparison})
        for key, value in data_json['data'].items():
            data_country['countries'].update({key : {}})
            data_country['countries'][key].update({'country' : value['country']})
        data_country.update({'now_id_session' : data_json['now_id_session']})
        data_country.update({'drow' : 'True'})
        return render(request, "../templates/country_comparison.html", data_country)
    data_json = str_to_json(id_session)
    context = {'countries': {}}
    for key, value in data_json['data'].items():
        context['countries'].update({key : {}})
        context['countries'][key].update({'country' : value['country']})
    context.update({'now_id_session' : data_json['now_id_session']})
    context.update({'drow' : 'False'})
    return render(request, "../templates/country_comparison.html", context)

def CountryValuation(request, id_session):
    data_json = str_to_json(id_session)
    context = {}
    context.update(data_json)
    if request.method == "POST":
        data_json = str_to_json(id_session)
        context = {'data': {}}
        context.update({'data' : data_json['now_id_session']})
        data = request.POST
        valuations = []
        cat = Category.objects.get(name = 'Valuation')
        vals = Metric.objects.filter(category = cat)
        field1 = data['ranking']
        field2 = data['valuation']
        for v in vals:
            valuations.append(v.code)

        if data['data_valuation'] == 'Chart':
            if data['ranking'] != 'Select type of country ranking' and data['valuation'] != 'Select valuation metric':
                chart = pygal.XY(stroke=False, explicit_size = 0.2, show_legend=False, 
                    human_readable=True, disable_xml_declaration= True, fill=True)

                list_for_chart = []
                field1 = data['ranking']
                field2 = data['valuation']

                data_json = str_to_json(id_session)
                metrics = list()
                vals = list()
                for iso,values in data_json['data'].items():
                    country = Country.objects.get(iso=iso)
                    metric = Metric.objects.get(code = field2)
                    cat = Category.objects.get(name = 'Valuation')
                    try:
                        value = Link.objects.get(country = country, metric = metric, category = cat)
                    except:
                        continue
                    vals.append(value.value)
                    if(field1 == 'Overall'):
                        selected1 = 'Overall country ranking'
                        metrics.append(values['Overall_ranking'])
                        a = (values['Overall_ranking'],value.value)
                    elif(field1 == 'Estimated'):
                        selected1 = 'Overall country ranking'
                        metrics.append(values['Estimated_ranking'])
                        a = (values['Estimated_ranking'],value.value)
                    list_for_chart.append(a)
                chart.title = field1 + ' rank' + '/' + field2
                chart.x_title= field1 + ' country ranking'
                chart.y_title= field2
                chart.add('',list_for_chart)
                data_json = str_to_json(id_session)
                context.update({'now_id_session' : data_json['now_id_session']})
                metrics = ['Overall country ranking', 'Estimated ranking based on GDP Per Capita']
                valuations = []
                cat = Category.objects.get(name = 'Valuation')
                vals = Metric.objects.filter(category = cat)
                for v in vals:
                    valuations.append(v.code)
                context.update({'drow' : 'False'})
                context.update({'metrics' : metrics})
                context.update({'valuations' : valuations})
                context.update({'chart': chart.render()})
                return render(request, "../templates/country_valuation.html", context)

    context.update({'now_id_session' : data_json['now_id_session']})
    metrics = ['Overall country ranking', 'Estimated ranking based on GDP Per Capita']
    valuations = []
    cat = Category.objects.get(name = 'Valuation')
    vals = Metric.objects.filter(category = cat)
    for v in vals:
        valuations.append(v.code)
    context.update({'metrics' : metrics})
    context.update({'valuations' : valuations})
    
    return render(request, "../templates/country_valuation.html", context)
