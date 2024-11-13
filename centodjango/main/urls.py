from rest_framework import  routers
from .api import StudentViewSet
from .views import StudentView
from django.urls import path, include

#router = routers.DefaultRouter()
##router.register('api/student', StudentViewSet, 'student')
#
#urlpatterns = router.urls

urlpatterns = [
    path('api/student', StudentView.as_view(), name='a')
]