from django.urls import path
from .views import BoardViewSet, TaskViewSet, CommentViewSet, EmailCheckView, TaskAssigneeView, TaskReviewerView, CommentRetrieveUpdateDestroy

urlpatterns = [
    path('email-check/', EmailCheckView.as_view(), name='email-check' ),
    path('boards/', BoardViewSet.as_view({'get': 'list', 'post': 'create'}), name='board-list-create' ),
    path('boards/<int:pk>/', BoardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='board-detail' ),
    path('tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='create-task' ),
    path('tasks/assigned-to-me/', TaskAssigneeView.as_view(), name='taskassigned-user' ),
    path('tasks/reviewing/', TaskReviewerView.as_view(), name='taskreviewing-user' ),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-detail' ),
    path('tasks/<int:task_id>/comments/', CommentViewSet.as_view(), name='tasklist-comments' ),
    path('tasks/<int:task_id>/comments/<int:pk>/', CommentRetrieveUpdateDestroy.as_view(), name='comment-detail' ), 
]