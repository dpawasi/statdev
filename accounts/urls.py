from django.conf.urls import url
from accounts import views


urlpatterns = [
    url(r'^$', views.UserProfile.as_view(), name='user_profile'),
    url(r'^update/$', views.UserProfileUpdate.as_view(), name='user_profile_update'),
    url(r'^addresses/create/(?P<type>\w+)/$', views.UserAddressCreate.as_view(), name='user_address_create'),
    url(r'^addresses/(?P<pk>\d+)/update/$', views.AddressUpdate.as_view(), name='address_update'),
    url(r'^addresses/(?P<pk>\d+)/delete/$', views.AddressDelete.as_view(), name='address_delete'),
    url(r'^organisations/create/$', views.OrganisationCreate.as_view(), name='organisation_create'),
    url(r'^organisations/(?P<pk>\d+)/update/$', views.OrganisationUpdate.as_view(), name='organisation_update'),
    url(r'^organisations/(?P<pk>\d+)/create-address/(?P<type>\w+)/$', views.OrganisationAddressCreate.as_view(), name='organisation_address_create'),
]
