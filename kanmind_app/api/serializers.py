from rest_framework import serializers
from django.contrib.auth.models import User
from kanmind_app.models import Task, Comment, Board


class UserInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','email','fullname']

    def get_fullname(self, obj):
        """
        Get the full name of the user, which is the username.

        Args:
            obj (User): The user instance.

        Returns:
            str: The username of the user.
        """
        return obj.username

class TaskSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        write_only=True,
        required=False, 
        allow_null=True
        )
    
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
        )
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'title', 'description','board','owner', 'status', 'priority', 'assignee','assignee_id', 'reviewer','reviewer_id', 'due_date', 'comments_count']
        
    def get_comments_count(self, obj):
        """
        Get the count of comments on the task.

        Args:
            obj (Task): The task instance.

        Returns:
            int: Number of comments.
        """
        return obj.comments.count()

    def create(self, validated_data):
        """
        Create a task and automatically set the authenticated user as owner.
        """
        request = self.context['request']
        validated_data['owner'] = request.user
        return super().create(validated_data)
        
        
    def validate(self, attrs):
        """
        Validate the task data, ensuring assignee and reviewer are not the same.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            ValidationError: If assignee and reviewer are the same.
        """
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        if assignee and reviewer and assignee == reviewer:
            raise serializers.ValidationError('Assignee and reviewer cannot be the same user')
        return attrs

class TaskDetailSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        write_only=True,
        required=False, 
        allow_null=True
        )
    
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
        )
    owner = UserInfoSerializer(read_only=True)
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description','board','owner', 'status', 'priority', 'assignee','assignee_id', 'reviewer','reviewer_id', 'due_date', 'comments_count']
        
    def comments_count(self):
        """
        Get the count of comments on the task.

        Returns:
            int: Number of comments.
        """
        return self.comments.count()
    
    def validate(self, attrs):
        """
        Validate the task data, ensuring assignee and reviewer are not the same.

        Args:
            attrs (dict): The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            ValidationError: If assignee and reviewer are the same.
        """
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        if assignee and reviewer and assignee == reviewer:
            raise serializers.ValidationError('Assignee and reviewer cannot be the same user')
        return attrs
    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        
    
    def get_author(self, obj):
        """
        Get the username of the comment author.

        Args:
            obj (Comment): The comment instance.

        Returns:
            str: The username of the author.
        """
        return obj.author.username

class BoardDetailReadSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(read_only=True)
    members = UserInfoSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks',
        ]
 
class BoardSerializer(serializers.ModelSerializer): 
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        write_only = True,
        allow_null=True,   
    )
    class Meta:
        model= Board
        fields = ['id', 'title','owner','owner_id','members', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']
            
    def create(self, validated_data):
        """create a Board with the current user as owner, add the usere automaticaaly as member

        Args:
            validated_data (Board): board instance

        Returns:
            Board: board instance
        """
        
        
        members = validated_data.pop('members', [])
        request = self.context['request']
        if members is None:
            members = []   
        board = Board.objects.create(owner=request.user, **validated_data)
        board.members.add(request.user) 

        if members:
            board.members.add(*members)

        return board
        
    def get_member_count(self, obj):
        """
        Get the count of members in the board.

        Args:
            obj (Board): The board instance.

        Returns:
            int: Number of members.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """
        Get the count of tasks (tickets) in the board.

        Args:
            obj (Board): The board instance.

        Returns:
            int: Number of tasks.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """
        Get the count of tasks with status 'to-do'.

        Args:
            obj (Board): The board instance.

        Returns:
            int: Number of to-do tasks.
        """
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """
        Get the count of tasks with high priority.

        Args:
            obj (Board): The board instance.

        Returns:
            int: Number of high priority tasks.
        """
        return obj.tasks.filter(priority='high').count()

class BoardPatchSerialiser(serializers.ModelSerializer):
    owner_data = UserInfoSerializer(source = 'owner',read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only = True,
        required=False
    )
    members_data = UserInfoSerializer(source='members', many=True, read_only=True)
    
    class Meta:
        model= Board
        fields = ['id', 'title','owner_data','members', 'members_data']
        
    def update(self, instance, validated_data):
        """Update the Board 

        Args:
            validated_data (Board): board instance

        Returns:
            Board: board instance
        """
        
        members = validated_data.pop('members', None)
        instance = super().update(instance, validated_data)

        if members is not None:
            instance.members.set(members)

        return instance
        
class CheckEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['id', 'email']
        
    
        
    