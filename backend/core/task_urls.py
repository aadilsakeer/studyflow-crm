from django.urls import path

from .task_views import (
    TaskDetailAPIView,
    TaskListCreateAPIView,
    TaskSummaryAPIView,
)

urlpatterns = [
    path(
        'summary/',
        TaskSummaryAPIView.as_view(),
        name='task-summary',
    ),
    path(
        '',
        TaskListCreateAPIView.as_view(),
        name='task-list',
    ),
    path(
        '<int:pk>/',
        TaskDetailAPIView.as_view(),
        name='task-detail',
    ),
]
