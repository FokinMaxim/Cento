from rest_framework import  routers
from rest_framework_simplejwt.views import TokenRefreshView
from .view.add_student_to_teacher_view import *
from .view.auth_views import *
from .view.check_homework import CheckVariantView
from .view.create_homework_view import CreateHomeworkView
from .view.get_assign_variants import get_assigned_variants
from .view.get_finance_info import LessonsPaidStatusView, TeacherFinancialStatsView
from .view.get_shedue_element_by_id import ScheduleElementDetailView, RecurringScheduleElementDetailView
from .view.get_shedue_elements_by_period import TeacherSchedulePeriodView, StudentSchedulePeriodView
from .view.get_student import getStudent
from .view.get_student_list_from_teacher import TeacherStudentsListView
from .view.get_upcomming_lessons_view import GetUpcomingLessonsView
from .view.lesson_views import *
from .view.profile_view import ProfileView
from .view.register_views import *
from .view.shedue_element_creation import ScheduleElementCreateView
from .view.task_views import *
from .view.variant_views import *
from django.urls import path, include
from .view.view_sets import *

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
    path('api/create-variant/', create_variant, name='create-variant'),

    path('api/combined-variants/', CombinedVariantsView.as_view(), name='combined-variants'),
    path('api/combined-tasks/', CombinedTasksView.as_view(), name='combined-tasks'),

    # Информация о профиле
    path('api/profile/', ProfileView.as_view(), name='profile'),

    path('api/create-homework/', CreateHomeworkView.as_view(), name='create-homework'),

    #получение вариантов
    path('api/variants/', get_all_variants, name='get-all-variants'),
    path('api/variants/<int:variant_id>/', get_variant_by_id, name='get-variant-by-id'),

    path('api/get-homework/', get_assigned_variants, name='get-assigned-variant'),

    path('api/check-variant/', CheckVariantView.as_view(), name='check-variant'),
    path('api/lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('api/lessons/<int:pk>/', LessonDeleteView.as_view(), name='lesson-delete'),
    path('api/get-upcoming-lessons/', GetUpcomingLessonsView.as_view(), name='get-upcoming-lessons'),

    path('api/students-of-teacher/', TeacherStudentsListView.as_view(), name='teacher-students'),

    path('api/schedule-elements/', ScheduleElementCreateView.as_view(), name='schedule-element-create'),
    path('api/schedule-elements/<int:pk>/', ScheduleElementDetailView.as_view(), name='schedule-element-detail'),
    path('api/recurring-schedules/<int:pk>/', RecurringScheduleElementDetailView.as_view(), name='recurring-schedule-detail'),

    path('api/teacher-period-schedule/', TeacherSchedulePeriodView.as_view(), name='teacher-schedule-period'),
    path('api/student-period-schedule/', StudentSchedulePeriodView.as_view(), name='student-schedule-period'),

    path('lessons/payment/', LessonsPaidStatusView.as_view(), name='teacher-payment-lessons'),
    path('finance/stats/', TeacherFinancialStatsView.as_view(), name='teacher-financial-stats'),

]
