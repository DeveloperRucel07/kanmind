from rest_framework import serializers
from kanmind_app.models import Task, Comment, Board
from django.contrib.auth import get_user_model
User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','email','fullname']

    def get_fullname(self, obj):
        return obj.username

class TaskSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = ['id', 'title', 'description','board','owner', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']
    def get_comments_count(self):
        return self.comments.count()
        
    def validate(self, attrs):
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        if assignee and reviewer and assignee == reviewer:
            raise serializers.ValidationError('Assignee and reviewer cannot be the same user')
        return attrs 

class TaskDetailSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assigned',
        queryset=User.objects.all(),
        write_only=True,
        required=False
        )
    
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False
        )
    
    assignee = UserInfoSerializer(source= 'assigned', read_only=True)
    reviewer = UserInfoSerializer(source= 'reviewer', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description','board','owner', 'status', 'priority', 'assignee','assignee_id', 'reviewer','reviewer_id', 'due_date', 'comments_count']
        
    def comments_count(self):
        return self.comments.count()
    
    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        
    ordering = ['-created_at']
    
    def get_author(self, obj):
        return obj.author.username
    
class BoardSerializer(serializers.ModelSerializer): 
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all() 
    )
    class Meta:
        model= Board
        fields = ['id', 'title', 'owner','members', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']
        read_only_fields = ['owner']
    
    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

class CheckEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['id', 'email']
        
    
        
    