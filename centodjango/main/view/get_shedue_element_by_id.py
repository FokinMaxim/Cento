# views/schedule_element_views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import ScheduleElement, RecurringScheduleElement
from ..serializer import ScheduleElementSerializer, RecurringScheduleElementSerializer
from ..permissions import IsTeacher, IsAssignedTo
from rest_framework.exceptions import PermissionDenied, ValidationError
from ..permissions import IsTeacher
from rest_framework.response import Response


class ScheduleElementDetailView(generics.RetrieveDestroyAPIView):
    queryset = ScheduleElement.objects.all()
    serializer_class = ScheduleElementSerializer
    permission_classes = [IsAuthenticated, IsAssignedTo]

    def get_object(self):
        obj = super().get_object()
        # Дополнительная проверка для учителя
        if self.request.user.role == 'учитель' and obj.teacher != self.request.user.teacher:
            raise PermissionDenied("Вы не являетесь учителем этого занятия")
        # Для учеников проверка через permission IsOwnerOrTeacher
        return obj

    def perform_destroy(self, instance):
        # Если это повторяющееся занятие - предлагаем удалить весь шаблон
        if instance.is_repetitive and instance.recurring_template:
            raise ValidationError({
                'detail': 'Это повторяющееся занятие',
                'recurring_template_id': instance.recurring_template.id,
                'suggestion': 'Удалите шаблон повторяющегося занятия вместо этого'
            })
        instance.delete()
        return Response({
            'detail': 'Занятие удалено',
        }, status=204)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class RecurringScheduleElementDetailView(generics.RetrieveDestroyAPIView):
    queryset = RecurringScheduleElement.objects.all()
    serializer_class = RecurringScheduleElementSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_object(self):
        obj = super().get_object()
        if obj.teacher != self.request.user.teacher:
            raise PermissionDenied("Вы не являетесь владельцем этого шаблона")
        return obj

    def perform_destroy(self, instance):
        # Удаляем все связанные занятия
        ScheduleElement.objects.filter(recurring_template=instance).delete()
        instance.delete()
        return Response({
            'detail': 'Шаблон и все связанные занятия удалены',
            'deleted_lessons_count': ScheduleElement.objects.filter(
                recurring_template=instance.id
            ).count()
        }, status=204)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)
