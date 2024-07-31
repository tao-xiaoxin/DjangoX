from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers.login import LoginSerializer


# Create your views here.
class LoginView(TokenObtainPairView):
    """
    登录接口
    """
    serializer_class = LoginSerializer
    permission_classes = []


