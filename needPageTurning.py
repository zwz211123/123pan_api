from api import PanAPI

api = PanAPI(token_file="access.json")

def get_share_list_all():
    limit = int(input("请输入每页文件数量 (最大不超过100): "))
    def get_share_list(limit ,nextPage_or_exit_in):             
        r = api.get_share_list(limit, nextPage_or_exit_in)
        share_list = r.get('shareList' ,[])
        if share_list:
            for share in share_list:
                print(f"\n  分享 ID: {share.get('shareId')}")
                print(f"  分享名称: {share.get('shareName')}")
                print(f"  分享码: {share.get('shareKey')}")
                print(f"  过期时间: {share.get('expiration')}")
                print(f"  是否失效: {'是' if share.get('expired') == 1 else '否'}")
                print(f"  分享链接提取码: {share.get('sharePwd') or '无'}")
            if r.get('lastShareId') != -1:
                nextPageStartId = r.get('lastShareId')
                nextPage_or_exit = input('还有下一页，是否翻页？(y翻页，回车退出)' or 'n')
                if nextPage_or_exit == 'y':
                    get_share_list(limit, nextPageStartId)
    get_share_list(limit, None)