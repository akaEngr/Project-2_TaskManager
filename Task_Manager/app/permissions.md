from pathlib import Path

content = r'''# Django REST Framework — Custom Permissions

## 1. What is a Permission?

A permission decides **who is allowed to access an API or perform an operation**.

Examples:
- Only Admin can perform CRUD.
- Normal users can only view data.
- Normal users can only update their own data.
- Normal users can create data but cannot delete it.

DRF provides built-in permissions, and we can create custom permissions using `BasePermission`.

---

## 2. Important Concepts

### `BasePermission`

```python
from rest_framework.permissions import BasePermission
```

A parent class used to create our own permission rules.

### `SAFE_METHODS`

```python
from rest_framework.permissions import SAFE_METHODS
```

Contains:

```python
("GET", "HEAD", "OPTIONS")
```

These methods are intended for reading data or checking API capabilities, rather than changing resources.

### `request.user.is_authenticated`

Checks whether a user is logged in.

- `True` → authenticated user
- `False` → anonymous user

### `request.user.is_staff`

Checks whether the user has Django staff status.

- `True` → staff user
- `False` → non-staff user

**Important:** `is_staff=True` does not necessarily mean the user is a superuser.

### `request.method`

Returns the HTTP method, such as:

```python
request.method == "GET"
request.method == "POST"
request.method == "PUT"
request.method == "PATCH"
request.method == "DELETE"
```

### `view.action`

For a DRF ViewSet, identifies the current action, such as:

```python
view.action == "list"
view.action == "retrieve"
view.action == "create"
view.action == "update"
view.action == "partial_update"
view.action == "destroy"
```

---

## 3. CRUD Operations

| Method | Action | Purpose |
|---|---|---|
| GET | List/Retrieve | Read data |
| POST | Create | Add data |
| PUT | Update | Replace/update the complete resource |
| PATCH | Partial update | Update selected fields |
| DELETE | Destroy | Delete data |

---

## 4. Common Permission Conditions

All examples below assume that `TaskView` is a DRF `ViewSet`.

### Condition 1: Only Admin Can Perform All CRUD

```python
from rest_framework.permissions import IsAdminUser

permission_classes = [IsAdminUser]
```

`IsAdminUser` permits users with `is_staff=True`.

- Anonymous user → Denied
- Normal user → Denied
- Staff user → Allowed

Use this when only staff should access the API.

### Condition 2: Normal Users Can Read; Admin Can Perform All CRUD

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS

class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in SAFE_METHODS:
                return True

            return request.user.is_staff

        return False
```

- Normal authenticated user → GET, HEAD, OPTIONS
- Staff user → All methods
- Anonymous user → Denied

This permits both listing and retrieving individual tasks for normal users.

### Condition 3: Normal Users Can Only Update; Admin Can Perform All CRUD

```python
from rest_framework.permissions import BasePermission

class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return request.method in ["PUT", "PATCH"]
```

- Normal authenticated user → PUT and PATCH
- Staff user → All methods
- Anonymous user → Denied

### Condition 4: Normal Users Can Only Create; Admin Can Perform All CRUD

```python
from rest_framework.permissions import BasePermission

class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return request.method == "POST"
```

- Normal authenticated user → POST
- Staff user → All methods
- Anonymous user → Denied

### Condition 5: Normal Users Can Only Delete; Admin Can Perform All CRUD

```python
from rest_framework.permissions import BasePermission

class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return request.method == "DELETE"
```

- Normal authenticated user → DELETE
- Staff user → All methods
- Anonymous user → Denied

### Condition 6: Normal Users Can Only Retrieve One Task; Admin Can Perform All CRUD

```python
from rest_framework.permissions import BasePermission

class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return (
            request.method == "GET"
            and view.action == "retrieve"
        )
```

- Normal authenticated user → GET `/tasks/1/`
- Staff user → All methods
- Anonymous user → Denied

Normal users cannot use the list action because `view.action` is `list`, not `retrieve`.

---

## 5. Permission Class for Each Condition

| Requirement | Permission |
|---|---|
| Admin only | `IsAdminUser` |
| Normal user can read; Admin can do all CRUD | `SAFE_METHODS` + `is_staff` |
| Normal user can update only | `request.method in ["PUT", "PATCH"]` |
| Normal user can create only | `request.method == "POST"` |
| Normal user can delete only | `request.method == "DELETE"` |
| Normal user can retrieve one task only | `GET` + `view.action == "retrieve"` |

Use only the permission class that matches your requirement.

---

## 6. Complete TaskView Example

This example allows:
- Admin/staff users to perform all CRUD operations.
- Normal users to update only their own tasks.
- Normal users to access only their own tasks if they have permission to access an object.

### `permissions.py`

```python
from rest_framework.permissions import BasePermission


class TaskPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return request.method in ["PUT", "PATCH"]
```

### `views.py`

```python
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import (
    JWTAuthentication,
    SessionAuthentication,
)

from .models import TaskModel
from .serializers import TaskSerializer
from .permissions import TaskPermission


class TaskView(ViewSet):

    authentication_classes = [
        JWTAuthentication,
        SessionAuthentication,
    ]

    permission_classes = [TaskPermission]

    def get_queryset(self):
        if self.request.user.is_staff:
            return TaskModel.objects.all()

        return TaskModel.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                {"msg": "Task Added Successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def list(self, request):
        tasks = self.get_queryset()

        paginator = PageNumberPagination()
        paginator.page_size = 4

        page = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        task = get_object_or_404(self.get_queryset(), id=pk)

        serializer = TaskSerializer(task)

        return Response(serializer.data)

    def update(self, request, pk=None):
        task = get_object_or_404(self.get_queryset(), id=pk)

        serializer = TaskSerializer(task, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({"msg": "Task Updated Successfully"})

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def partial_update(self, request, pk=None):
        task = get_object_or_404(self.get_queryset(), id=pk)

        serializer = TaskSerializer(
            task,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response({"msg": "Task Updated Successfully"})

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, pk=None):
        task = get_object_or_404(self.get_queryset(), id=pk)

        task.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
```

---

## 7. Does CRUD Code Need to Change?

Usually, **no**. If you only change who is allowed to perform an operation, you can keep your existing CRUD methods and change:

```python
permission_classes = [TaskPermission]
```

However, a permission class only controls access. It does not automatically implement CRUD functionality.

- `create()` creates data.
- `list()` returns the list and applies your manual pagination.
- `retrieve()` returns one object.
- `update()` updates the full object.
- `partial_update()` updates selected fields.
- `destroy()` deletes the object.

Keep your existing methods, serializers, model, and URL router as appropriate.

---

## 8. Important Security Notes

1. **Permissions do not filter data.** Use `get_queryset()` to control which records a user can access.
2. In the example above, normal users can update only their own tasks because `get_queryset()` filters by `user=self.request.user`.
3. `IsAdminUser` means staff users, not exclusively superusers.
4. A normal user allowed to use `PUT` or `PATCH` is not automatically restricted to particular fields. Use serializer validation if some fields must not be changed.
5. Browsable API and Thunder Client both obey the same permission rules. Session authentication or a valid JWT is needed to authenticate requests.

## 9. Final Rule to Remember

**Authentication asks:** Who are you?

**Permission asks:** What are you allowed to do?

**Queryset asks:** Which records are you allowed to access?

These three concepts work together to secure your Django REST Framework API.
'''
path = Path("/mnt/data/DRF_Permissions_Notes.md")
path.write_text(content, encoding="utf-8")
print(f"Created: {path}\nSize: {path.stat().st_size} bytes")
