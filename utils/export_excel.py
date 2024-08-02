# 导出excel数据
import hashlib
import os
import time

import xlrd
import xlwt
from django.conf import settings
from utils.common import getfulldomian


def len_byte(value):
    # 获取字符串长度，一个中文的长度为2
    length = len(value)
    utf8_length = len(value.encode('utf-8'))
    length = (utf8_length - length) / 2 + length
    return int(length)


def export_excel(request, field_data: list, data: list, FileName: str, file_path: str = settings.MEDIA_ROOT):
    """
    Excel导出
    :param request: 请求request
    :param data: 数据源
    :param field_data: 首行数据源（表头）
    :param file_path: 文件保存路径（默认保存在media路径）
    :param FileName: 文件保存名字
    :return:返回文件的下载url完整路径
    """
    wbk = xlwt.Workbook(encoding='utf-8')
    sheet = wbk.add_sheet('Sheet1', cell_overwrite_ok=True)  # 第二参数用于确认同一个cell单元是否可以重设值。
    style = xlwt.XFStyle()  # 赋值style为XFStyle()，初始化样式
    # 设置居中
    wbk.set_colour_RGB(0x23, 0, 60, 139)
    xlwt.add_palette_colour("custom_colour_35", 0x23)
    tab_al = xlwt.Alignment()
    tab_al.horz = 0x02  # 设置水平居中
    tab_al.vert = 0x01  # 设置垂直居中
    # 设置表头单元格背景颜色
    tab_pattern = xlwt.Pattern()  # 创建一个模式
    tab_pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置其模式为实型
    tab_pattern.pattern_fore_colour = 55
    # 设置单元格内字体样式
    tab_fnt = xlwt.Font()  # 创建一个文本格式，包括字体、字号和颜色样式特性
    tab_fnt.height = 200
    default_width = 14
    tab_fnt.name = u'楷体'  # 设置其字体为微软雅黑
    tab_fnt.colour_index = 1  # 设置其字体颜色
    # 设置单元格下框线样式
    tab_borders = xlwt.Borders()
    tab_borders.left = xlwt.Borders.THIN
    tab_borders.right = xlwt.Borders.THIN
    tab_borders.top = xlwt.Borders.THIN
    tab_borders.bottom = xlwt.Borders.THIN
    tab_borders.left_colour = 23
    tab_borders.right_colour = 23
    tab_borders.bottom_colour = 23
    tab_borders.top_colour = 23
    #### 把数据写入excel中
    # 所有表格单元格样式
    # 先生成表头
    style.alignment = tab_al  # 设置居中
    style.pattern = tab_pattern  # 设置表头单元格背景颜色
    style.font = tab_fnt  # 设置单元格内字体样式
    style.borders = tab_borders
    for index, ele in enumerate(field_data):
        sheet.write_merge(0, 0, index, index, ele, style)  # (列开始, 列结束, 行开始, 行结束, '数据内容')

    # 确定栏位宽度
    col_width = []
    for index, ele in enumerate(data):
        for inx, values in enumerate(ele.values()):
            if index == 0:
                col_width.append(len_byte(str(values)))
            else:
                if col_width[inx] < len_byte(str(values)):
                    col_width[inx] = len_byte(str(values))
    # 设置栏位宽度，栏位宽度小于10时候采用默认宽度
    for i in range(len(col_width)):
        if col_width[i] > 10:
            width = col_width[i] if col_width[i] < 36 else 36
            sheet.col(i).width = 256 * (width + 6)
        else:
            sheet.col(i).width = 256 * (default_width)

    row = 1
    # 内容背景颜色
    left_pattern = xlwt.Pattern()  # 创建一个模式
    left_pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置其模式为实型
    left_pattern.pattern_fore_colour = 1

    # 设置单元格内字体样式
    left_fnt = xlwt.Font()  # 创建一个文本格式，包括字体、字号和颜色样式特性
    left_fnt.height = 200
    left_fnt.name = u'楷体'  # 设置其字体为微软雅黑
    left_fnt.colour_index = 0  # 设置其字体颜色

    left_style = style
    left_style.pattern = left_pattern
    left_style.font = left_fnt

    for results in data:
        for index, values in enumerate(results.values()):
            sheet.write(row, index, label=values, style=left_style)
        row += 1

    monthTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    pathRoot = os.path.join(file_path, 'systemexport', monthTime)
    if not os.path.exists(pathRoot):
        os.makedirs(pathRoot)
    path_name = os.path.join(pathRoot, FileName)
    wbk.save(path_name)
    return getfulldomian(request) + settings.MEDIA_URL + 'systemexport' + "/" + monthTime + "/" + FileName
    # return os.path.join('system', monthTime, FileName)


def excel_to_data(file_url, field_data):
    """
    读取导入的excel文件
    :param request:
    :param field_data: 首行数据源
    :param data: 数据源
    :param FilName: 文件名
    :return:
    """
    # 读取excel 文件
    data = xlrd.open_workbook(os.path.join(settings.BASE_DIR.replace('\\', os.sep), *file_url.split(os.sep)))
    table = data.sheets()[0]
    # 创建一个空列表，存储Excel的数据
    tables = []
    for i, rown in enumerate(range(table.nrows)):
        if i == 0: continue
        array = {}
        for index, ele in enumerate(field_data.keys()):
            cell_value = table.cell_value(rown, index)
            # 由于excel导入数字类型后，会出现数字加 .0 的，进行处理
            if type(cell_value) is float and str(cell_value).split('.')[1] == '0':
                cell_value = int(str(cell_value).split('.')[0])
            if type(cell_value) is str:
                cell_value = cell_value.strip(' \t\n\r')
            array[ele] = cell_value

        tables.append(array)
    return tables
#
# # 导出excel数据
# import os
# import time
# import bson
# import xlwt
# import openpyxl
# from django.conf import settings
# import pandas as pd
# from dimension.libs.ali_oss import AliOss
# from openpyxl.styles import PatternFill
# from openpyxl.styles import Alignment
# from openpyxl.styles import Side, Border, colors, Font
# from openpyxl.utils import get_column_letter
# from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
#
# ALI_OSS = AliOss()
#
#
# def len_byte(value):
#     '''
#     excel 表格的宽度串长度，一个中文的长度为2
#     try:
#         length = len(value)
#         utf8_length = len(value.encode('utf-8'))
#         length = (utf8_length - length) / 2 + length
#     except Exception as e:
#         length = 20
#     return int(length)
#
#
# def deal_str(data):
#     '''
#     处理csv较长数字数据导出后变成科学计数法
#
#     '''
#     # 获取字符    '''
#     data = str(data) + '\t'
#     return data
#
#
# def check_str(value):
#     '''
#     将None转为空字符串
#     '''
#     value = ILLEGAL_CHARACTERS_RE.sub(r'', str(value))
#     if value == 'None' or not value:
#         return ''
#     else:
#         return value
#
#
# def export_xls(field_data: list, data: list, file_path: str = settings.BASE_DIR):
#     """
#     将数据导出xls
#     :param data: 数据源
#     :param field_data: 首行数据源
#     :param file_path: 文件保存路径
#     :param FileName: 文件保存名字
#     :return:
#     """
#     wbk = xlwt.Workbook(encoding='utf-8')
#     sheet = wbk.add_sheet('Sheet1', cell_overwrite_ok=True)  # 第二参数用于确认同一个cell单元是否可以重设值。
#     style = xlwt.XFStyle()  # 赋值style为XFStyle()，初始化样式
#     # 设置居中
#     wbk.set_colour_RGB(0x23, 0, 60, 139)
#     xlwt.add_palette_colour("custom_colour_35", 0x23)
#     tab_al = xlwt.Alignment()
#     tab_al.horz = 0x02  # 设置水平居中
#     tab_al.vert = 0x01  # 设置垂直居中
#     # 设置表头单元格背景颜色
#     tab_pattern = xlwt.Pattern()  # 创建一个模式
#     tab_pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置其模式为实型
#     tab_pattern.pattern_fore_colour = 55
#     # 设置单元格内字体样式
#     tab_fnt = xlwt.Font()  # 创建一个文本格式，包括字体、字号和颜色样式特性
#     tab_fnt.height = 200
#     default_width = 14
#     tab_fnt.name = u'宋体'  # 设置其字体为微软雅黑
#     tab_fnt.colour_index = 1  # 设置其字体颜色
#     # 设置单元格下框线样式
#     tab_borders = xlwt.Borders()
#     tab_borders.left = xlwt.Borders.THIN
#     tab_borders.right = xlwt.Borders.THIN
#     tab_borders.top = xlwt.Borders.THIN
#     tab_borders.bottom = xlwt.Borders.THIN
#     tab_borders.left_colour = 23
#     tab_borders.right_colour = 23
#     tab_borders.bottom_colour = 23
#     tab_borders.top_colour = 23
#     #### 把数据写入excel中
#     # 所有表格单元格样式
#     # 先生成表头
#     style.alignment = tab_al  # 设置居中
#     style.pattern = tab_pattern  # 设置表头单元格背景颜色
#     style.font = tab_fnt  # 设置单元格内字体样式
#     style.borders = tab_borders
#     for index, ele in enumerate(field_data):
#         sheet.write_merge(0, 0, index, index, ele, style)  # (列开始, 列结束, 行开始, 行结束, '数据内容')
#
#     # 确定栏位宽度
#     col_width = []
#     for index, ele in enumerate(data):
#         for inx, values in enumerate(ele.values()):
#             if index == 0:
#                 col_width.append(len_byte(str(values)))
#             else:
#                 if col_width[inx] < len_byte(str(values)):
#                     col_width[inx] = len_byte(str(values))
#     # 设置栏位宽度，栏位宽度小于10时候采用默认宽度
#     for i in range(len(col_width)):
#         if col_width[i] > 10:
#             width = col_width[i] if col_width[i] < 36 else 36
#             sheet.col(i).width = 256 * (width + 6)
#         else:
#             sheet.col(i).width = 256 * (default_width)
#
#     row = 1
#     # 内容背景颜色
#     left_pattern = xlwt.Pattern()  # 创建一个模式
#     left_pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置其模式为实型
#     left_pattern.pattern_fore_colour = 1
#
#     # 设置单元格内字体样式
#     left_fnt = xlwt.Font()  # 创建一个文本格式，包括字体、字号和颜色样式特性
#     left_fnt.height = 200
#     left_fnt.name = u'宋体'  # 设置其字体为微软雅黑
#     left_fnt.colour_index = 0  # 设置其字体颜色
#
#     left_style = style
#     left_style.pattern = left_pattern
#     left_style.font = left_fnt
#
#     for results in data:
#         for index, values in enumerate(results.values()):
#             sheet.write(row, index, label=values, style=left_style)
#         row += 1
#     filename = f"{bson.ObjectId()}.xls"
#     execl_path = os.path.join(file_path, "tmp", "excel", )
#     if not os.path.exists(execl_path):
#         os.makedirs(execl_path)
#     path_name = os.path.join(execl_path, filename)
#     wbk.save(path_name)
#     file_url = ALI_OSS.excel_upload(path_name, f"tmp/excel/", filename)
#     try:
#         os.remove(path_name)
#     except FileNotFoundError:
#         pass
#     return file_url
#
#
# def export_xlsx(field_data: list, data: list, file_path: str = settings.BASE_DIR):
#     """
#     将数据导出xlsx
#     :param data:
#     :param path:
#     :return:
#     """
#     # 实例化一个wrokbook
#     wbk = openpyxl.Workbook()
#     sheet = wbk.active
#     # 为sheet命名,默认为Sheet
#     # sheet.title = 'Sheet1'
#     # 设置所有边框加粗
#     border = Border(top=Side(border_style='thin', color=colors.BLACK),
#                     bottom=Side(border_style='thin', color=colors.BLACK),
#                     left=Side(border_style='thin', color=colors.BLACK),
#                     right=Side(border_style='thin', color=colors.BLACK))
#     # 设置表格居中显示
#     align = Alignment(horizontal='center', vertical='center')
#     # 设置字体
#     font = Font(name="宋体")
#     # 设置背景色
#     fill_title = PatternFill(start_color="D9D9D9", fill_type="solid")
#     fill_content = PatternFill(start_color="E2EFDA", fill_type="solid")
#     # 确定栏位宽度
#     col_width = []
#     for index, ele in enumerate(data):
#         for inx, values in enumerate(ele.values()):
#             if index == 0:
#                 col_width.append(len_byte(str(values)))
#             else:
#                 if col_width[inx] < len_byte(str(values)):
#                     col_width[inx] = len_byte(str(values))
#     # 写标题的第一行
#     for index, item in enumerate(field_data):
#         sheet.cell(row=1, column=index + 1, value=item).border = border
#         sheet.cell(row=1, column=index + 1, value=item).alignment = align
#         sheet.cell(row=1, column=index + 1, value=item).font = font
#         sheet.cell(row=1, column=index + 1, value=item).fill = fill_title
#     # 设置栏位宽度
#     for i in range(len(col_width)):
#         letter = get_column_letter(i + 1)  # 列字母
#         sheet.column_dimensions[letter].width = col_width[i] * 1.2 + 4  # 也就是列宽为最大长度*1.2 可以自己调整
#     # 准备写入数据
#     row = 1
#     for results in data:
#         for index, values in enumerate(results.values()):
#             sheet.cell(row=row + 1, column=index + 1, value=str(check_str(values))).font = font
#             sheet.cell(row=row + 1, column=index + 1, value=str(check_str(values))).border = border
#             sheet.cell(row=row + 1, column=index + 1, value=str(check_str(values))).alignment = align
#             sheet.cell(row=row + 1, column=index + 1, value=str(check_str(values))).fill = fill_content
#         row += 1
#     time_stamp = int(time.time())
#     execl_path = os.path.join(file_path, "tmp", "excel", )
#     if not os.path.exists(execl_path):
#         os.makedirs(execl_path)
#     # 生成文件名
#     filename = "{}.xlsx".format(bson.ObjectId())
#     path_name = os.path.join(execl_path, filename)
#     # 写入到文件
#     wbk.save(path_name)
#     file_url = ALI_OSS.excel_upload(path_name, f"tmp/excel/{time_stamp}/", filename)
#     try:
#         os.remove(path_name)
#     except FileNotFoundError:
#         pass
#     return file_url
#
#
# def export_csv(field_data, value_list):
#     '''
#     pandas 导出csv
#     '''
#     data_list = list()
#     for results in value_list:
#         data = [deal_str(check_str(values)) for index, values in enumerate(results.values())]
#         data_list.append(data)
#     file_name = "{}.csv".format(bson.ObjectId())
#     file_path = os.path.join(settings.BASE_DIR, "tmp", "excel", )
#     file_path = file_path + f"/{file_name}"
#     df = pd.DataFrame(columns=field_data, data=data_list)
#     # 导出csv
#     df.to_csv(file_path, encoding='utf_8_sig')
#     file_url = ALI_OSS.excel_upload(file_path, f"tmp/excel/", file_name)
#     try:
#         os.remove(file_path)
#     except FileNotFoundError:
#         pass
#     return file_url
#
#
# def export_table(field_data, value_list):
#     '''
#     根据导出数据量导出格式不同
#     :parma: field_data 表格表头
#     :parma: value_list 表格行列表
#     '''
#
#     count = len(value_list)
#     if count <= 2000:
#         file_url = export_xlsx(field_data, value_list)
#     elif 2000 < count <= 20000:
#         file_url = export_xls(field_data, value_list)
#     else:
#         '''导出csv文本'''
#         file_url = export_csv(field_data, value_list)
#     return file_url
#
