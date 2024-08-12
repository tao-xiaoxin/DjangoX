from user.models import Users  # type: ignore
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import argparse


class GenerateTokenSerializer(TokenObtainPairSerializer):
    """
    token序列化器:
    重写djangorestframework-simplejwt的序列化器
    """

    @classmethod
    def get_token(cls, user):
        refresh = super(GenerateTokenSerializer, cls).get_token(user)
        data = {}
        data['identity'] = user.identity
        data['user_id'] = user.user_id
        data["user_name"] = user.username
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


def generate_token(user_id):
    """
    快速生成用户jwt token:
    python manage.py runscript generate_token --script-args <用户ID>
    """
    try:
        user = Users.objects.get(user_id=user_id)
        userinfo = GenerateTokenSerializer.get_token(user)
        print(userinfo)
    except Users.DoesNotExist:
        print("用户不存在")


def run(*args):
    parser = argparse.ArgumentParser(description='生成用户JWT Token')
    parser.add_argument('userid', type=str, help='用户ID')
    args = parser.parse_args(args[0])
    generate_token(args.userid)
