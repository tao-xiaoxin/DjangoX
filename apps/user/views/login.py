from rest_framework.generics import GenericAPIView
from utils.json_response import DetailResponse, ErrorResponse
from ..serializers.login import LoginSerializer


# Create your views here.

class LoginView(GenericAPIView):
    """
    登录接口
    """
    serializer_class = LoginSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid(raise_exception=True):
            return ErrorResponse(serializer.errors)
        data = serializer.context.get('data')
        return DetailResponse(msg="登录成功！", data=data)
