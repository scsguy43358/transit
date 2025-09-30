from django.urls import path
from . import views, auth_views

urlpatterns = [
    path("api/health/", views.health),
    path("api/routes/", views.routes),
    path("api/eta/", views.eta),
    path("api/predictions/", views.predictions),
    path("api/schedule/", views.schedule),
    path("api/operator/routes/", views.operator_push_routes),

    # Auth endpoints
    path("api/auth/register/", auth_views.register),
    path("api/auth/login/", auth_views.login),
    path("api/auth/mfa/enroll/", auth_views.mfa_enroll),
    path("api/auth/mfa/confirm/", auth_views.mfa_confirm),
    path("api/auth/mfa/disable/", auth_views.mfa_disable),

    # New endpoints
    path("api/route-mapping/", views.get_route_mapping),
    path("api/passengers/", views.passenger_predictions),
]
