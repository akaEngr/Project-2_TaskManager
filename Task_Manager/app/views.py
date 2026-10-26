from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .throttle import RegisterThrottle, LoginThrottle
from .models import TaskModel
from .serializers import TaskSerializer
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination


class RegisterView(ViewSet):
    throttle_classes = [RegisterThrottle]
    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg" : "Account Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(ViewSet):
    throttle_classes = [LoginThrottle]
    
    def create(self, request):
        serailizer = LoginSerializer(data=request.data)
        if serailizer.is_valid():
            user = authenticate(request,
                username = serailizer.validated_data["username"],                            
                password = serailizer.validated_data["password"]                            
                )
            if user is None:
                return Response({"msg" : "Invalid username and password"}, status=status.HTTP_401_UNAUTHORIZED)
            refresh_token = RefreshToken.for_user(user)
            return Response({
                "msg" : "Login Successful",
                "access_token" : str(refresh_token.access_token),
                "refreshe_token" : str(refresh_token)

                })
        return Response(serailizer.errors ,status=status.HTTP_400_BAD_REQUEST)
            


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
        
class TaskView(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = []   #. IMP : if not usong using then use it blank

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id", "title", "is_completed"]
    ordering_fields = ["id", "title", "is_completed"]
    ordering = ["id"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return TaskModel.objects.all()
        return TaskModel.objects.filter(user=self.request.user)

        
    def list(self, request):
        tasks = self.get_queryset()

        for backend_class in self.filter_backends:
            backend = backend_class()   #. IMP : ()
            tasks = backend.filter_queryset(request, tasks, self) #. IMP : order


        paginator = PageNumberPagination()
        paginator.page_size = 2
        tasks = paginator.paginate_queryset(tasks, request, self)

        serializer = TaskSerializer(tasks, many=True)
        return paginator.get_paginated_response(serializer.data)     

        #/ return Response(serializer.data)
         
    def retrieve(self, request, pk=None):
        if pk is not None:
            task = get_object_or_404(self.get_queryset(), id=pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)          
        return Response({"msg":"Invalid inputs"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"msg" : "Task Added Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        if pk is not None:
            task = get_object_or_404(self.get_queryset(), id=pk)   #. IMP 
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
              
                # task["title"] = serializer.validated_data["title"]  #. IMP : use task.title (task is a model instance) not task["title"] (this is used for dictionary)

                task.title = serializer.validated_data["title"]
                task.description = serializer.validated_data["description"]
                task.is_completed = serializer.validated_data["is_completed"]
                task.save()

                #/ or
                #/ serializer.save()
                

                return Response({"msg" : "Task updated successfully"}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg":"Invalid inputs"}, status=status.HTTP_400_BAD_REQUEST)



    def partial_update(self, request, pk=None):
            if pk is not None:
                task = get_object_or_404(self.get_queryset(), id=pk)   #. IMP 
                serializer = TaskSerializer(task, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"msg" : "Task updated successfully"}, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"msg":"Invalid inputs"}, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
            if pk is not None:
                task = get_object_or_404(self.get_queryset(), id=pk)   #. IMP 
                task.delete()
                return Response({"msg" : "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"msg":"Invalid inputs"}, status=status.HTTP_400_BAD_REQUEST)




