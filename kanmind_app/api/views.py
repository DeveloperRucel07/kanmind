from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .permissions import IsBoardOwnerOrMember, CanDeleteTask, IsAssigneeOrReviewerTask, IsOwnerAndDeleteOnly, CanManageComment, CanReadTask, CanManageTask
from django.db.models import Q
from kanmind_app.models import Board, Task, Comment
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import CheckEmailSerializer, BoardSerializer, User, TaskSerializer, TaskDetailSerializer, CommentSerializer


class BoardViewSet(ModelViewSet):
    permission_classes = [IsBoardOwnerOrMember, IsAuthenticated ]
    serializer_class = BoardSerializer
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
    def perform_create(self, serializer):
         serializer.save(owner = self.request.user)
        # board.members.add(self.request.user) 
    
    
class TaskViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated,  CanDeleteTask, CanReadTask, CanManageTask ]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    # def get_queryset(self):
    #     user = self.request.user
    #     return Task.objects.filter(Q(board__owner=user) | Q(board__members=user)).distinct()
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentViewSet(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CanManageComment]
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        return Comment.objects.filter(Q(task = task))
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        serializer.save(author=self.request.user, task=task)

class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CanManageComment]
    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(Q(author = user))
    
    
class TaskAssigneeView(generics.ListAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsAssigneeOrReviewerTask, CanManageTask]
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(assignee=user))
    
    
class TaskReviewerView(generics.ListAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsAssigneeOrReviewerTask]
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(reviewer=user))

class EmailCheckView(generics.ListAPIView):
    permission_classes  = [IsAuthenticated]
    serializer_class = CheckEmailSerializer
    
    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "Email query parameter is required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found"},status=status.HTTP_404_NOT_FOUND
        )
        data = {
            "fullname": user.username,
            "email": user.email,
            "user_id": user.id,
        }
        return Response(data, status=status.HTTP_200_OK)
    
    # def post(self, request, *args, **kwargs):
    #     serializer = CheckEmailSerializer(data=request.data)
    #     if serializer.is_valid():
    #         email = serializer.validated_data['email']
    #         try:
    #             account_found = User.objects.get(email=email)
    #         except User.DoesNotExist:
    #             return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    #         data = {
    #             'fullname': account_found.username,
    #             'email': account_found.email,
    #             'user_id': account_found.id,
    #         }
    #         return Response(data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, {'detail': 'An Email muss be provided'}, status=status.HTTP_400_BAD_REQUEST)
