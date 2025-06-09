from django.urls import path
from .views import RunDLCView

urlpatterns = [
    path('run/', RunDLCView.as_view(), name='run_dlc'),
]