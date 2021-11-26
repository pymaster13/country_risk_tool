from django.urls import path

from .views import UploadView, TableView, TableSession, RankingAll, RankingCategory, \
RankingESG, RankingSDG, CountryInfo, CountryComparison, CountryValuation


urlpatterns = [
    path('table/<id_session>/ranking/', RankingAll , name='rank_all'),
    path('table/<id_session>/ranking/category/', RankingCategory , name='rank_category'),
    path('table/<id_session>/ranking/ESG/', RankingESG , name='rank_ESG'),
    path('table/<id_session>/ranking/SDG/', RankingSDG , name='rank_SDG'),
    path('table/<id_session>/comparison/', CountryComparison , name='country_comparison'),
    path('table/<id_session>/valuation/', CountryValuation , name='country_valuation'),
    path('table/<id_session>/<iso>/', CountryInfo , name='country_info'),
    path('table/<id_session>/', TableSession, name='table_session'),
    path('table/', TableView , name='table'),
   
    path('upload/', UploadView.as_view() , name='upload'),
]
