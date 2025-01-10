import os
import json
import time
import requests
from functions.share_functions import get_share_list, update_share_info, create_share_link  # 导入分享功能模块
from functions.file_management import get_file_list, get_file_detail, print_file_detail, move_files, rename_files, trash_files, delete_files, recover_files  # 导入文件管理功能模块

CLIENT_ID = "3fc58cfe32d24fcdb35f373caa9c6ca8"  # 替换为实际的 client_id
CLIENT_SECRET = "b6a0d571f969456da302dd10c5dff7f1"  # 替换为实际的 client_secret
TOKEN_FILE = '.\\python\\123pan_api\\access_token.json'

def get_access_token(client_id, client_secret):
    url = "https://open-api.123pan.com/api/v1/access_token"
    headers = {"platform": "open_platform"}
    body = {
        "clientID": client_id,
        "clientSecret": client_secret
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                access_token = data['data'].get("accessToken")
                expired_at = data['data'].get("expiredAt")
                print("请求成功！获取到 Access Token。")
                print("Access Token:", access_token)
                print("过期时间:", expired_at)
                save_access_token(access_token, expired_at)
                return access_token, expired_at
            else:
                print("请求失败，返回信息:", data.get("message"))
                return None, None
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
            return None, None
    except Exception as e:
        print("发生错误:", e)
        return None, None

def save_access_token(access_token, expired_at):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'access_token': access_token, 'expired_at': expired_at}, f)

def load_access_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            access_token = data.get('access_token')
            expired_at = data.get('expired_at')
            if access_token and expired_at:
                if time.time() < time.mktime(time.strptime(expired_at, "%Y-%m-%dT%H:%M:%S%z")):
                    return access_token
                else:
                    print("Access Token 已过期，需重新获取。")
            else:
                print("Access Token 数据不完整，需重新获取。")
    else:
        print("没有找到 Access Token 文件，需获取新 Token。")
    return None

def main():
    has_token = input("您是否已有有效的 Access Token? (y/n): ").strip().lower()

    if has_token == 'y':
        access_token = load_access_token()
        if access_token:
            print("已加载 Access Token:", access_token)
        else:
            access_token, _ = get_access_token(CLIENT_ID, CLIENT_SECRET)
    else:
        access_token, _ = get_access_token(CLIENT_ID, CLIENT_SECRET)

    while True:
        print("\n欢迎使用云盘 API")
        print("1. 分享功能")
        print("2. 文件管理")
        print("0. 退出程序")

        choice = input("请选择操作（0-2）：")

        if choice == '1':
            while True:
                print("\n请选择分享功能：")
                print("1. 获取分享文件列表")
                print("2. 更新分享链接信息")
                print("3. 创建分享链接")
                print("0. 返回主菜单")

                share_choice = input("请输入选项（0-3）：")

                if share_choice == '1':
                    limit = int(input("请输入每页文件数量（最大不超过100）："))
                    last_share_id = input("请输入翻页查询的 lastShareId（可选，回车跳过）：")
                    last_share_id = int(last_share_id) if last_share_id else None
                    get_share_list(access_token, limit, last_share_id)

                elif share_choice == '2':
                    share_id_list = input("请输入分享链接ID列表（以逗号分隔）：").split(',')
                    share_id_list = [int(id) for id in share_id_list]
                    traffic_switch = input("请输入免登录流量包开关 (1: 关闭, 2: 打开，可选，回车跳过)：")
                    traffic_switch = int(traffic_switch) if traffic_switch else None
                    traffic_limit_switch = input("请输入免登录流量限制开关 (1: 关闭, 2: 打开，可选，回车跳过)：")
                    traffic_limit_switch = int(traffic_limit_switch) if traffic_limit_switch else None
                    traffic_limit = input("请输入免登陆限制流量（单位：字节，可选，回车跳过）：")
                    traffic_limit = int(traffic_limit) if traffic_limit else None
                    update_share_info(access_token, share_id_list, traffic_switch, traffic_limit_switch, traffic_limit)

                elif share_choice == '3':
                    share_name = input("请输入分享链接名称：")
                    share_expire = input("请输入分享链接有效期天数 (1、7、30、0)：")
                    file_id_list = input("请输入分享文件ID列表（以逗号分隔）：")
                    share_pwd = input("请输入分享链接提取码（可选，回车跳过）：")
                    traffic_switch = input("请输入免登录流量包开关 (1: 关闭, 2: 打开，可选，回车跳过)：")
                    traffic_switch = int(traffic_switch) if traffic_switch else None
                    traffic_limit_switch = input("请输入免登录流量限制开关 (1: 关闭, 2: 打开，可选，回车跳过)：")
                    traffic_limit_switch = int(traffic_limit_switch) if traffic_limit_switch else None
                    traffic_limit = input("请输入免登陆限制流量（单位：字节，可选，回车跳过）：")
                    traffic_limit = int(traffic_limit) if traffic_limit else None
                    create_share_link(access_token, share_name, share_expire, file_id_list, share_pwd, traffic_switch, traffic_limit_switch, traffic_limit)

                elif share_choice == '0':
                    print("返回主菜单。")
                    break

                else:
                    print("无效的选项，请重新输入。")

        elif choice == '2':
            while True:
                print("\n请选择文件管理功能：")
                print("1. 获取文件列表")
                print("2. 获取文件详情")
                print("3. 移动文件")
                print("4. 重命名文件")
                print("5. 删除文件至回收站")
                print("6. 彻底删除文件")
                print("7. 从回收站恢复文件")
                print("0. 返回主菜单")

                file_choice = input("请输入选项（0-7）：")

                if file_choice == '1':
                    parent_file_id = int(input("请输入要查询的目录 ID（根目录为 0）："))
                    limit = int(input("请输入每页文件数量（最大不超过100）："))
                    search_data = input("请输入搜索关键字（可选，回车跳过）：") or None
                    search_mode = input("请输入搜索模式 (0: 全文模糊搜索, 1: 精准搜索，可选，回车跳过)：")
                    search_mode = int(search_mode) if search_mode else None
                    last_file_id = input("请输入翻页查询的 lastFileId（可选，回车跳过）：")
                    last_file_id = int(last_file_id) if last_file_id else None

                    last_file_id = get_file_list(access_token, parent_file_id, limit, search_data, search_mode, last_file_id)

                elif file_choice == '2':
                    file_id = int(input("请输入文件 ID 获取详细信息："))
                    file_detail = get_file_detail(access_token, file_id)
                    if file_detail:
                        print_file_detail(file_detail)

                elif file_choice == '3':
                    file_ids_input = input("请输入要移动的文件 ID 列表（以逗号分隔）：")
                    file_ids = [int(id.strip()) for id in file_ids_input.split(',')]
                    to_parent_file_id = int(input("请输入要移动到的目标文件夹 ID（根目录为 0）："))
                    move_files(access_token, file_ids, to_parent_file_id)

                elif file_choice == '4':
                    rename_input = input("请输入文件 ID 和新的文件名（格式：文件ID|新文件名，多个文件用逗号分隔）：")
                    rename_list = []
                    for item in rename_input.split(','):
                        file_id, new_name = item.split('|')
                        rename_list.append(f"{file_id.strip()}|{new_name.strip()}")
                    rename_files(access_token, rename_list)

                elif file_choice == '5':
                    file_ids_input = input("请输入要删除的文件 ID 列表（以逗号分隔）：")
                    file_ids = [int(id.strip()) for id in file_ids_input.split(',')]
                    trash_files(access_token, file_ids)

                elif file_choice == '6':
                    file_ids_input = input("请输入要彻底删除的文件 ID 列表（以逗号分隔）：")
                    file_ids = [int(id.strip()) for id in file_ids_input.split(',')]
                    delete_files(access_token, file_ids)

                elif file_choice == '7':
                    file_ids_input = input("请输入要恢复的文件 ID 列表（以逗号分隔）：")
                    file_ids = [int(id.strip()) for id in file_ids_input.split(',')]
                    recover_files(access_token, file_ids)

                elif file_choice == '0':
                    print("返回主菜单。")
                    break
                else:
                    print("无效的选项，请重新输入。")

        elif choice == '0':
            print("退出程序。")
            break

        else:
            print("无效的选项，请重新输入。")

if __name__ == "__main__":
    main()
