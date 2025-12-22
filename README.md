# KanMind

KanMind is a Django-based task management application built with Django REST Framework. It allows users to create boards, manage tasks, assign reviewers, and collaborate on projects.

## Features

- User authentication and registration
- Board creation and management
- Task creation, assignment, and status tracking
- Comment system for tasks
- Role-based permissions (owner, member, assignee, reviewer)
- RESTful API endpoints

## Tech Stack

- **Python**: "3.11+"
- **Backend**: "Django>=5.0,<6.0"
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite
- **Authentication**: Token-based authentication, authentication with email and password

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DeveloperRucel07/kanmind.git
   cd kanmind
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`.

## API Endpoints

### Authentication
- `POST /api/registration/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout

### Boards
- `GET /api/boards/` - List boards (owned or member)
- `POST /api/boards/` - Create a new board
- `GET /api/boards/{id}/` - Retrieve a board
- `PUT /api/boards/{id}/` - Update a board
- `DELETE /api/boards/{id}/` - Delete a board

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/{id}/` - Retrieve a task
- `PUT /api/tasks/{id}/` - Update a task
- `DELETE /api/tasks/{id}/` - Delete a task
- `GET /api/tasks/assignee/` - List tasks assigned to user
- `GET /api/tasks/reviewer/` - List tasks where user is reviewer

### Comments
- `GET /api/tasks/{task_id}/comments/` - List comments for a task
- `POST /api/tasks/{task_id}/comments/` - Create a comment
- `GET /api/tasks/{task_id}/comments/{id}/` - Retrieve a comment
- `PUT /api/tasks/{task_id}/comments/{id}/` - Update a comment
- `DELETE /tasks/{task_id}/api/comments/{id}/` - Delete a comment

### Utilities
- `GET /api/check-email/` - Check if email exists

## Usage

1. Register a new user or login with existing credentials.
2. Create a board and add members.
3. Create tasks within boards, assign them, and set reviewers.
4. Add comments to tasks for collaboration.
5. Update task status as work progresses.

## Models

- **Board**: Represents a project board with owner and members.
- **Task**: Represents a task with status, priority, assignee, reviewer, and due date.
- **Comment**: Represents comments on tasks.
- **User**: Django's built-in user model with token authentication.

## Permissions

- Board owners can manage boards and delete tasks.
- Board members can read and manage tasks.
- Task assignees and reviewers have specific access.
- Comment authors can edit their own comments.


