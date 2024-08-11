# -*- coding: utf-8 -*-

"""
@Remark: 自定义图片上传
"""
import os
import datetime
from django.conf import settings
from .common import renameuploadimg, getfulldomian
from configs.config import DOMAIN_HOST


def file_upload(request, dirs):
    """
    request: 请求
    dirs: 要上传到那个目录
    """
    files = request.FILES.getlist('file')
    msg = {}
    if not files:
        msg['code'] = 400
        msg['msg'] = "上传的文件不能为空"
        return msg

    invalid_files = []
    valid_files = []

    allowed_content_types = [
        'image/', 'video/', 'audio/',
        'application/pdf',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'audio/mpeg'
    ]

    allowed_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.flv',
        '.pdf', '.xls', '.xlsx', '.doc', '.docx', '.txt', '.mp3'
    )

    try:
        for file in files:
            file_name = file.name
            file_extension = os.path.splitext(file_name)[1].lower()

            if not any(file.content_type.startswith(type) for type in
                       allowed_content_types) or file_extension not in allowed_extensions:
                invalid_files.append(file_name)
                continue

            if file.size > 1024 * 500000:
                msg['code'] = 400
                msg['msg'] = "文件大小不能超过500M"
                return msg

            curr_time = datetime.datetime.now()
            new_file_name = renameuploadimg(file_name)  # 您可能想要重命名这个函数为更通用的名称
            time_path = curr_time.strftime("%Y-%m-%d")
            file_task_dir = dirs
            sub_path = os.path.join(settings.MEDIA_ROOT, file_task_dir, time_path)
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)
            file_path = os.path.join(sub_path, new_file_name)
            web_file_url = DOMAIN_HOST + settings.MEDIA_URL + file_task_dir + "/" + time_path + "/" + new_file_name

            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            valid_files.append(web_file_url)

        if invalid_files:
            msg['code'] = 400
            msg['msg'] = '请检查是否支持的文件，失败文件部分如下：{0}'.format(','.join(invalid_files[:10]))
            return msg

        msg['code'] = 200
        msg['files'] = valid_files
        msg['msg'] = '上传成功'
        return msg

    except Exception as e:
        msg['code'] = 400
        msg['msg'] = f'上传失败: {str(e)}'
        return msg
