from django.urls import path, re_path
from rest_framework import routers

system_url = routers.SimpleRouter()

urlpatterns = [
    # re_path('operation_log/deletealllogs/',OperationLogViewSet.as_view({'delete':'deletealllogs'})),

]
urlpatterns += system_url.urls
