from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from kanmind_app.models import Board, Task, Comment
from .permissions import IsBoardOwnerOrMember, CanDeleteTask, IsAssigneeOrReviewerTask, IsOwnerAndDeleteOnly, CanManageComment, CanReadTask, CanManageTask
from .serializers import CheckEmailSerializer, BoardSerializer, User,BoardDetailReadSerializer, TaskDetailSerializer, CommentSerializer, BoardPatchSerialiser, TaskSerializer


class BoardListCreateViewSet(generics.ListCreateAPIView):
    permission_classes = [ IsAuthenticated]
    serializer_class = BoardSerializer
    def get_queryset(self):
        """
        Get the queryset of boards that the authenticated user owns or is a member of.

        Returns:
            QuerySet: Boards owned by or accessible to the user.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()


class BoardRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBoardOwnerOrMember, IsAuthenticated, IsOwnerAndDeleteOnly]
    queryset  = Board.objects.all()

    def get_serializer_class(self):
        """
        Select the read serializer for GET,
        and the write serializer (with owner_data & members_data) for PATCH/PUT.
        """
        if self.request.method in ('PATCH', 'PUT'):
            return BoardPatchSerialiser
        return BoardDetailReadSerializer
    def perform_create(self, serializer):
        """
        Create a new board and add the authenticated user as a member.

        Args:
            serializer (BoardSerializer): The serializer instance with validated data.
        """
        board = serializer.save(owner = self.request.user)
        board.members.add(self.request.user)
    
    
class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated,  CanDeleteTask, CanReadTask, CanManageTask ]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    
    # def get_serializer_class(self):
    #     """
    #     Select the read serializer for GET,
    #     and the write serializer (with owner_data & members_data) for PATCH/PUT.
    #     """
    #     if self.request.method in ('GET', 'OPTIONS'):
    #         return TaskDetailSerializer
    #     return TaskSerializer
    
class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,  CanDeleteTask, CanReadTask, CanManageTask ]
    serializer_class = TaskDetailSerializer
    queryset = Task.objects.all()


class CommentViewSet(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CanManageComment]
    
    def get_queryset(self):
        """
        Get the queryset of comments for the specified task.

        Returns:
            QuerySet: Comments associated with the task. and ordered comments.
        """
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        return Comment.objects.filter(Q(task = task)).order_by("-created_at")
    
    def perform_create(self, serializer):
        """
        Create a new comment for the specified task with the authenticated user as the author.

        Args:
            serializer (CommentSerializer): The serializer instance with validated data.
        """
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        serializer.save(author=self.request.user, task=task)

class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CanManageComment]
    def get_queryset(self):
        """
        Get the queryset of comments authored by the authenticated user.

        Returns:
            QuerySet: Comments authored by the user.
        """
        user = self.request.user
        return Comment.objects.filter(Q(author = user))
    
    
class TaskAssigneeView(generics.ListAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsAssigneeOrReviewerTask, CanManageTask]
    def get_queryset(self):
        """
        Get the queryset of tasks assigned to the authenticated user.

        Returns:
            QuerySet: Tasks where the user is the assignee.
        """
        user = self.request.user
        return Task.objects.filter(Q(assignee=user))
       
class TaskReviewerView(generics.ListAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsAssigneeOrReviewerTask]
    def get_queryset(self):
        """
        Get the queryset of tasks where the authenticated user is the reviewer.

        Returns:
            QuerySet: Tasks where the user is the reviewer.
        """
        user = self.request.user
        return Task.objects.filter(Q(reviewer=user))

class EmailCheckView(generics.ListAPIView):
    permission_classes  = [IsAuthenticated]
    serializer_class = CheckEmailSerializer
    
    def get(self, request, *args, **kwargs):
        """
        Check if a user exists by email and return their information.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: User data if found, error message otherwise.
        """
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
            "id": user.id,
        }
        return Response(data, status=status.HTTP_200_OK)

