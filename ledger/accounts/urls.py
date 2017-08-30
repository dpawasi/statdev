from django.conf.urls import url, include
from ledger.accounts import views 

urlpatterns = [
    url(r'^$', views.UserProfile.as_view(), name='user_profile'),
    url(r'^done/$', views.done, name='done'),
    url(r'^validation-sent/$', views.validation_sent, name='validation_sent'),
    url(r'^token-login/(?P<token>[^/]+)/(?P<email>[^/]+)/$', views.token_login, name='token_login'),
    url(r'^logout/', views.logout, name='logout'),

]
