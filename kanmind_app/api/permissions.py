from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanmind_app.models import Board, Task, Comment
from django.db.models import Q


def user_can_read_task(user, task):
    board = task.board
    return (
        board.owner == user
        or board.members.filter(id=user.id).exists()
    )

class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
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
        user = request.user
        if request.method == 'DELETE':
            return obj.owner == user or obj.author == user
        return False

class CanReadTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return user_can_read_task(user, obj)
        return False

class IsAssigneeOrRevierwerTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return obj.assignee == user or obj.reviewer == user
        return False


class CanManageTask(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method == "POST":
            board_id = request.data.get("board")
            if not board_id:
                return False
            return Board.objects.filter(id=board_id ).filter( Q(owner=user) | Q(members=user)).exists()

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board

        if request.method in SAFE_METHODS:
            return user_can_read_task(user, obj)

        if request.method in ["PUT", "PATCH"]:
            return user_can_read_task(user, obj)

        if request.method == "DELETE":
            return board.owner == user or obj.owner == user
        return False

class CanDeleteTask(BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        if request.method in SAFE_METHODS:
            return user_can_read_task(user, obj)
        elif request.method == "DELETE":
            return obj.owner == user or board.owner == user
        return obj.owner == user or board.owner == user
    

class CanManageComment(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        task_id = view.kwargs.get("task_id")
        if not task_id:
            return False
        
        try:
            task = Task.objects.select_related("board").get(id=task_id)
        except Task.DoesNotExist:
            return False
        
        return user_can_read_task(user, task)

    def has_object_permission(self, request, view, obj):
        user = request.user
        task = obj.task

        if request.method in SAFE_METHODS:
            return user_can_read_task(user, task)

        if request.method in ["PUT", "PATCH"]:
            return obj.author == user

        if request.method == "DELETE":
            return obj.author == user or task.board.owner == user

        return False