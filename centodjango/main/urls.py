from rest_framework import  routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *
from django.urls import path, include

router = routers.DefaultRouter()
router.register('api/student', StudentViewSet, 'student')
router.register('api/teacher', TeacherViewSet, 'teacher')
router.register('api/tariff', TariffViewSet, 'tariff')
router.register('api/exam', ExamViewSet, 'exam')
router.register('api/variant', VariantViewSet, 'variant')
router.register('api/task', TaskViewSet, 'task')
router.register('api/task_type', TypeOfTaskViewSet, 'task_type')
router.register('api/teacher_variant_student', TeachersVariantStudentViewSet, 'teacher_variant_student')

#urlpatterns = router.urls #vfrtynjc2005
urlpatterns = [
    path('', include(router.urls)),

    # Регистрация
    path('api/register/', RegisterView.as_view(), name='register'),

    path('api/register/student/', RegisterStudentView.as_view(), name='register-student'),
    path('api/register/teacher/', RegisterTeacherView.as_view(), name='register-teacher'),

    # Аутентификация
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Получение полной информации об ученике
    path('api/get-student/<int:student_id>/', getStudent, name='get-student'),
    # Добавление ученика учителю
    path('api/add-student/', AddStudentToTeacherView.as_view(), name='add-student'),
    #Добавление задания
    path('api/create-task/', create_task, name='create-task'),

    path('api/combined-variants/', CombinedVariantsView.as_view(), name='combined-variants'),
    path('api/combined-tasks/', CombinedTasksView.as_view(), name='combined-tasks'),

    # Информация о профиле
    path('api/profile/', ProfileView.as_view(), name='profile'),
]
