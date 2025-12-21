from django.urls import path
from .views import BoardListCreateViewSet,BoardRetrieveUpdateDestroy, TaskRetrieveUpdateDestroyView, CommentViewSet, EmailCheckView,TaskListCreateView ,TaskAssigneeView, TaskReviewerView, CommentRetrieveUpdateDestroy

urlpatterns = [
    path('email-check/', EmailCheckView.as_view(), name='email-check' ),
    path('boards/', BoardListCreateViewSet.as_view(), name='board-list-create' ),
    path('boards/<int:pk>/', BoardRetrieveUpdateDestroy.as_view(), name='board-detail' ),
    path('tasks/', TaskListCreateView.as_view(), name='create-task' ),
    path('tasks/assigned-to-me/', TaskAssigneeView.as_view(), name='taskassigned-user' ),
    path('tasks/reviewing/', TaskReviewerView.as_view(), name='taskreviewing-user' ),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail' ),
    path('tasks/<int:task_id>/comments/', CommentViewSet.as_view(), name='tasklist-comments' ),
    path('tasks/<int:task_id>/comments/<int:pk>/', CommentRetrieveUpdateDestroy.as_view(), name='comment-detail' ), 
]