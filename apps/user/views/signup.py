from rest_framework.generics import GenericAPIView
from ..serializers.signup_serializers import SignUpSerializer
from utils.json_response import SuccessResponse, ErrorResponse


class SignUpView(GenericAPIView):
    """
    注册接口
    """
    serializer_class = SignUpSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return SuccessResponse(msg="注册成功！")
        return ErrorResponse(msg="注册失败！")
