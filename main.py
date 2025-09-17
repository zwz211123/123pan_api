import os
import sys
from api import PanAPI
from needPageTurning import *

def print_main_menu():
    """打印主菜单"""
    print("\n欢迎使用123云盘 API")
    print("1. 分享功能")
    print("2. 文件管理")
    print("3. 直链功能")
    print("0. 退出程序")

def print_share_menu():
    """打印分享功能菜单"""
    print("\n选择分享功能:")
    print("1. 获取分享列表")
    print("2. 更新分享信息")
    print("3. 创建分享链接")
    print("0. 返回主菜单")

def print_file_menu():
    """打印文件管理菜单"""
    print("\n选择文件管理功能:")
    print("1. 获取文件列表")
    print("2. 查看文件详情")
    print("3. 移动文件")
    print("4. 重命名文件")
    print("5. 将文件移至回收站")
    print("6. 永久删除文件")
    print("7. 从回收站恢复文件")
    print("0. 返回主菜单")

def print_direct_link_menu():
    """打印直链功能菜单"""
    print("\n选择直链功能:")
    print("1. 启用文件直链")
    print("2. 禁用文件直链")
    print("3. 获取文件直链")
    print("0. 返回主菜单")

def handle_share_functions(api):
    """处理分享功能"""
    while True:
        print_share_menu()
        share_choice = input("请输入选项 (0-3): ")
        
        if share_choice == '0':
            break
        
        elif share_choice == '1':
            # 获取分享列表
            get_share_list_all()
        
        elif share_choice == '2':
            # 更新分享信息
            share_id_list = input("请输入分享链接ID列表 (以逗号分隔): ")
            while not share_id_list:
                print('输入无效')
                share_id_list = input("请输入分享链接ID列表 (以逗号分隔): ")

            try:
                share_id_list = [int(id) for id in share_id_list.split(',')]
            except ValueError:
                print('请输入正确的ID（数字）')
            
            traffic_switch = int(input("请输入免登录流量包开关 (1: 关闭, 2: 打开，可选，回车跳过): ") or "1")
            
            traffic_limit_switch = None
            traffic_limit = None
            
            if traffic_switch == 2:
                traffic_limit_switch = int(input("请输入免登录流量限制开关 (1: 关闭, 2: 打开，可选，回车跳过): ") or "1")
                
                if traffic_limit_switch == 2:
                    traffic_limit = int(input("请输入免登录流量限制值 (单位：字节，可选，回车跳过): ") or "0")
            
            api.update_share_info(share_id_list, traffic_switch, traffic_limit_switch, traffic_limit)
        
        elif share_choice == '3':
            # 创建分享链接
            file_id_list = input("请输入文件ID列表 (以逗号分隔): ")
            while not file_id_list:
                print('输入无效')
                file_id_list = input("请输入文件ID列表 (以逗号分隔): ")
            file_id_list = [int(id) for id in file_id_list.split(',')]
            
            share_name = input("请输入分享链接名称: ")
            share_expire = int(input("请输入分享链接有效期天数 (1, 7, 30, 0表示永久): "))
            share_pwd = input("请输入分享链接提取码 (可选，回车跳过): ")
            
            traffic_switch = int(input("请输入免登录流量包开关 (1: 关闭, 2: 打开，可选，回车跳过): ") or "1")
            
            traffic_limit_switch = 1
            traffic_limit = None
            
            if traffic_switch == 2:
                traffic_limit_switch = int(input("请输入免登录流量限制开关 (1: 关闭, 2: 打开，可选，回车跳过): ") or "1")
                
                if traffic_limit_switch == 2:
                    traffic_limit = int(input("请输入免登录流量限制值 (单位：字节，可选，回车跳过): ") or "0")
            
            api.create_share_link(file_id_list, share_name, share_expire, share_pwd, traffic_switch, traffic_limit_switch, traffic_limit)
        
        else:
            print("无效选项，请重新输入")

def handle_file_functions(api):
    """处理文件管理功能"""
    while True:
        print_file_menu()
        file_choice = input("请输入选项 (0-7): ")
        
        if file_choice == '0':
            break
        
        elif file_choice == '1':
            # 获取文件列表
            parent_file_id = int(input("请输入父文件夹ID (默认为0，表示根目录): ") or "0")
            limit = int(input("请输入每页文件数量 (最大不超过100): ") or "100")
            search_data = input("请输入搜索关键词 (可选，回车跳过): ")
            search_data = search_data if search_data else None
            
            search_mode = input("请输入搜索模式 (可选，回车跳过): ")
            search_mode = search_mode if search_mode else None
            
            last_file_id = input("请输入上一页最后一个文件ID (可选，回车跳过): ")
            last_file_id = int(last_file_id) if last_file_id else None
            
            file_list, last_file_id = api.get_file_list(parent_file_id, limit, search_data, search_mode, last_file_id)
            
            if file_list:
                for file in file_list:
                    # 解析文件信息
                    file_id = file.get('fileID')
                    filename = file.get('filename')
                    file_type = '文件夹' if file['type'] == 0 else '文件'
                    size = file.get('size', 0)
                    etag = file.get('etag', '')
                    
                    print(f"\n  文件ID: {file_id}")
                    print(f"  文件名: {filename}")
                    print(f"  类型: {file_type}")
                    print(f"  大小: {size} 字节")
                    print(f"  ETag: {etag}")
                
                print(f"\n最后一个文件ID: {last_file_id}")
        
        elif file_choice == '2':
            # 查看文件详情
            try:
                file_id = int(input("请输入文件ID: "))
            except ValueError:
                print('输入无效')
                continue
            api.print_file_detail(file_id)
        
        elif file_choice == '3':
            # 移动文件
            file_ids = input("请输入要移动的文件ID列表 (以逗号分隔): ")
            try:
                file_ids = [int(id) for id in file_ids.split(',')]
            except ValueError:
                print('输入无效')
                continue
            
            target_parent_id = int(input("请输入目标父文件夹ID: "))
            api.move_files(file_ids, target_parent_id)
        
        elif file_choice == '4':
            # 重命名文件
            try:
                file_id = int(input("请输入文件ID: "))
            except ValueError:
                print('输入无效')
                continue
            new_name = input("请输入新文件名: ")
            api.rename_files(file_id, new_name)
        
        elif file_choice == '5':
            # 将文件移至回收站
            file_ids = input("请输入要移至回收站的文件ID列表 (以逗号分隔): ")
            try:
                file_ids = [int(id) for id in file_ids.split(',')]
            except ValueError:
                print('输入无效')
                continue
            api.trash_files(file_ids)
        
        elif file_choice == '6':
            # 永久删除文件
            file_ids = input("请输入要永久删除的文件ID列表 (以逗号分隔): ")
            try:
                file_ids = [int(id) for id in file_ids.split(',')]
            except ValueError:
                print('输入无效')
                continue
            api.delete_files(file_ids)
        
        elif file_choice == '7':
            # 从回收站恢复文件
            file_ids = input("请输入要从回收站恢复的文件ID列表 (以逗号分隔): ")
            try:
                file_ids = [int(id) for id in file_ids.split(',')]
            except ValueError:
                print('输入无效')
                continue
            api.recover_files(file_ids)
        
        else:
            print("无效选项，请重新输入")

def handle_direct_link_functions(api):
    """处理直链功能"""
    while True:
        print_direct_link_menu()
        direct_choice = input("请输入选项 (0-3): ")
        
        if direct_choice == '0':
            break
        
        elif direct_choice == '1':
            # 启用文件直链
            try:
                file_id = int(input("请输入文件ID: "))
            except ValueError:
                print('输入无效')
                continue                
            api.enable_direct_link(file_id)
        
        elif direct_choice == '2':
            # 禁用文件直链
            try:
                file_id = int(input("请输入文件ID: "))
            except ValueError:
                print('输入无效')
                continue
            api.disable_direct_link(file_id)
        
        elif direct_choice == '3':
            # 获取文件直链
            try:
                file_id = int(input("请输入文件ID: "))
            except ValueError:
                print('输入无效')
                continue
            api.get_direct_link(file_id)
        
        else:
            print("无效选项，请重新输入")

def main():
    """主函数"""
    # 创建API实例，默认从access.json读取凭证
    api = PanAPI(token_file="access.json")
    
    # 确保有有效的access_token
    access_token = api.ensure_token()
    if not access_token:
        print("无法获取有效的Access Token，请检查凭证是否正确")
        return
    
    while True:
        print_main_menu()
        choice = input("请输入选项 (0-3): ")
        
        if choice == '0':
            print("感谢使用，再见！")
            break
        
        elif choice == '1':
            handle_share_functions(api)
        
        elif choice == '2':
            handle_file_functions(api)
        
        elif choice == '3':
            handle_direct_link_functions(api)
        
        else:
            print("无效选项，请重新输入")

if __name__ == "__main__":
    main()
