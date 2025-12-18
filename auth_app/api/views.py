from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user = user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email
            }
        else:
            data = serializer.errors
        
        return Response(data)
       

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()  # Token löschen
        return Response({"detail": "Logout erfolgreich. Token wurde gelöscht."}, status=status.HTTP_200_OK)