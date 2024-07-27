from rest_framework.generics import GenericAPIView
from ..serializers.signup import SignUpSerializer
from utils.validator import handle_serializer_validation
from utils.json_response import DetailResponse, ErrorResponse


class SignUpView(GenericAPIView):
    """
    注册接口
    """
    serializer_class = SignUpSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            o_users = serializer.create(request.data)
            return DetailResponse(msg="注册成功！")
        return handle_serializer_validation(serializer)
