from django.db import models
from django.contrib.auth.models import User



class Board(models.Model):
    title = models.CharField(max_length=55)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_board')
    members = models.ManyToManyField(User, related_name='boards')
    def member_count(self):
        return self.members.count()

    def ticket_count(self):
        return self.tasks.count()

    def tasks_to_do_count(self):
        return self.tasks.filter(status="to-do").count()

    def tasks_high_prio_count(self):
        return self.tasks.filter(priority="high").count()

class Task(models.Model):
    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks' )
    owner= models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_task')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='to-do')
    priority = models.CharField(max_length=20, choices = PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks', null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='review_tasks', null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    def comments_count(self):
        return self.comments.count()




class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Comment by {self.author.username}"
    



