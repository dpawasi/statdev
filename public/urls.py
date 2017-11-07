from django.conf.urls import url
from public import views

urlpatterns = [
                  url(r'^public/applications/(?P<action>\w+)/$', views.PublicApplicationsList.as_view(), name='public_application_list'),
                  url(r'^public/application/(?P<pk>\d+)/(?P<action>\w+)/$', views.PublicApplicationFeedback.as_view(), name='public_application'),
              ]

