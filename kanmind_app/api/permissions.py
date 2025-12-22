from rest_framework.permissions import BasePermission, SAFE_METHODS


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
        
        if request.method =="POST":
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
        task = obj.task

        if request.method in SAFE_METHODS:
            return user_can_read_task(user, task)
        
        if request.method =="POST":
            return user_can_read_task(user, task)
        
        if request.method == "DELETE":
            return obj.author == user or task.board.owner == user

        return False
