from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.shortcuts import get_object_or_404
from kanmind_app.models import Board, Task

def user_can_read_task(user, task):
    """
        Check whether a user can read a task.
        A user can read a task if they are:
        - The board owner
        - A board member
        Args:
            user (User): Authenticated user.
            task (Task): Task instance.
            
        Returns:
        bool: True if user has read access.
    """
    board = task.board
    return (
        board.owner == user
        or board.members.filter(id=user.id).exists()
    )

class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner or a member of the board for object-level permissions.

        Args:
            request (Request): The HTTP request object.
            view: The view that is being accessed.
            obj: The board object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        user = request.user
        if request.method in SAFE_METHODS:
            return (obj.owner == user or obj.members.filter(id=user.id).exists())
        elif request.method =="POST":
            return (obj.owner == user or obj.members.filter(id=user.id).exists())
        elif request.method == "DELETE":
            return obj.owner == user
        return obj.owner == user

class IsOwnerAndDeleteOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Allow deletion only if the user is the owner or author of the object.

        Args:
            request (Request): The HTTP request object.
            view: The view that is being accessed.
            obj: The object (board or comment).

        Returns:
            bool: True if the user can delete, False otherwise.
        """
        user = request.user
        if request.method == 'DELETE':
            return obj.owner == user or obj.author == user
        return True

class CanReadTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Check if the user can read the task for safe methods.

        Args:
            request (Request): The HTTP request object.
            view: The view that is being accessed.
            obj (Task): The task object.

        Returns:
            bool: True if the user can read the task, False otherwise.
        """
        user = request.user
        if request.method in SAFE_METHODS:
            return user_can_read_task(user, obj)
        return False

class IsAssigneeOrReviewerTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the assignee or reviewer of the task for safe methods.

        Args:
            request (Request): The HTTP request object.
            view: The view that is being accessed.
            obj (Task): The task object.

        Returns:
            bool: True if the user is assignee or reviewer, False otherwise.
        """
        user = request.user
        if request.method in SAFE_METHODS:
            return obj.assignee == user or obj.reviewer == user
        return False

class CanManageTask(BasePermission):
    def has_permission(self, request, view):
        """give permission to create a task if the user is member of the Board or not.
        Also check if the Board exist or not.

        Args:
            view (task): Task LIst create View

        Raises:
            ValidationError: if the board was not give
            NotFound: if the give board wass not found
            PermissionDenied: if the user don't have right access

        Returns:
            bool: True if everything is OK
        """
        
        if request.method != 'POST':
            return True
        board_id = request.data.get('board')
        if not board_id:
            raise ValidationError({"detail": "Board is required to create Task here"})
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board does not exist.")
        user = request.user
        if board.owner != user and not board.members.filter(id=user.id).exists():
            raise PermissionDenied("You are not a member of this Board")
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permission for managing a specific task.

        Args:
            request (Request): The HTTP request object.
            view: The view that is being accessed.
            obj (Task): The task object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        user = request.user
        board = obj.board

        if request.method in SAFE_METHODS:
            return user_can_read_task(user, obj)

        if request.method =="PATCH":
            return user_can_read_task(user, obj)
        
        if request.method == "DELETE":
            return board.owner == user or obj.owner == user
        
class CanDeleteTask(BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Check if the user can delete the task.

        Args:
            request (Request): The HTTP request object.
            view: The view that is being accessed.
            obj (Task): The task object.

        Returns:
            bool: True if the user can delete, False otherwise.
        """
        user = request.user
        board = obj.board
        if request.method in SAFE_METHODS:
            return user_can_read_task(user, obj)
        elif request.method == "DELETE":
            return obj.owner == user or board.owner == user
        return obj.owner == user
    
class CanManageComment(BasePermission):
    
    def has_permission(self, request, view):
        """
            Allows comment creation only if the user is a member or owner of the board.
        """
        task_id = view.kwargs.get('task_id')
        if not task_id:
            raise NotFound("Task ID is missing.")
        task = get_object_or_404(Task, id=task_id)
        board = task.board
        user = request.user
        if board.owner == user or board.members.filter(id=user.id).exists():
            return True
        raise PermissionDenied("You must be a board member to perform this action")

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permission for managing a specific comment.

        Args:
            request (Request): The HTTP request object.
            view: The view that is being accessed.
            obj (Comment): The comment object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        user = request.user
        if request.method in ["PATCH", "PUT", "DELETE"]:
            if obj.author == user:
                return True
            raise PermissionDenied("You are not the Author for this comment.")
        return True
