import json
import requests
import rumps
from LeetCodeNotifier import GenshinNotifier


class LeetCodeStatusBarApp(rumps.App):
    url = "https://leetcode-cn.com/graphql/"
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'authorization': '',
        'origin': 'https://leetcode-cn.com',
        'referer': 'https://leetcode-cn.com/study-plan/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome', / '96.0.4664.110 Safari/537.36",
    }
    
    def __init__(self):
        super(LeetCodeStatusBarApp, self).__init__("LeetCode", icon='LeetCode.png', quit_button="退出")
        self.resin_notifier = GenshinNotifier(40)
        self.resin_full_notifier = GenshinNotifier(160, GenshinNotifier.NOTIFY_TYPE_UNTIL)
        
        self.user_info = []
        self.plan_progress = []
        self.today_status = []
        
        rumps.Timer(self.refresh, 60 * 2).start()
        
        
    def _update_menu(self):
        self.menu.clear()
        menu = []
        menu += self.user_info
        menu += self.today_status
        menu += [None]
        menu += self.plan_progress
        menu += [None]
        menu += [rumps.MenuItem("刷新", self.refresh), self.quit_button]
        self.menu = menu
    
    def refresh(self, sender):
        self._update_info()
        self._update_plans()
        self._update_today_status()
        self._update_menu()
    
    def _update_info(self):
        data = {
            "query": "\n    query globalData {\n  userStatus {\n    isSignedIn\n    isPremium\n    username\n    realName\n    avatar\n    userSlug\n    isAdmin\n    useTranslation\n    premiumExpiredAt\n    isTranslator\n    isSuperuser\n    isPhoneVerified\n    isVerified\n  }\n  jobsMyCompany {\n    nameSlug\n  }\n  commonNojPermissionTypes\n}\n    ",
            "variables": {}}
        res = self._req(data)
        if res.status_code == 200:
            self.user_info = [rumps.MenuItem(f"ID: {res.json()['data']['userStatus']['realName']}", self._do_nothing)]
        else:
            self.user_info = f'ID 加载失败 ({res})'

    def _update_today_status(self):
        data = {"query":"\n    query questionOfToday {\n  todayRecord {\n    date\n    userStatus\n    question {\n      questionId\n      frontendQuestionId: questionFrontendId\n      difficulty\n      title\n      titleCn: translatedTitle\n      titleSlug\n      paidOnly: isPaidOnly\n      freqBar\n      isFavor\n      acRate\n      status\n      solutionNum\n      hasVideoSolution\n      topicTags {\n        name\n        nameTranslated: translatedName\n        id\n      }\n      extra {\n        topCompanyTags {\n          imgUrl\n          slug\n          numSubscribed\n        }\n      }\n    }\n    lastSubmission {\n      id\n    }\n  }\n}\n    ","variables":{}}
        res = self._req(data)
        if res.status_code == 200:
            status = res.json()['data']['todayRecord'][0]['userStatus']
            date = res.json()['data']['todayRecord'][0]['date']
            
            self.today_status = [
                rumps.MenuItem("今日已打卡" if status == 'FINISH' else status, self._do_nothing),
                rumps.MenuItem(date),
            ]
        else:
            self.today_status = f'状态加载失败 ({res})'
    
    def _update_plans(self):
        data = {"query":"\n    query planProgressOngoing {\n  planOngoingProgress: planOngoingProgresses(limit: 100) {\n    daysPassed\n    questionNum\n    completedNum\n    endAt\n    id\n    startedAt\n    plan {\n      name\n      slug\n      awarded\n      days\n      medal {\n        config {\n          icon\n          iconGif\n          iconGifBackground\n          iconWearing\n        }\n        name\n      }\n      group {\n        cover\n        slug\n        name\n      }\n    }\n  }\n}\n    "}
        res = self._req(data)
        
        if res.status_code != 200:
            self.plan_progress = [f'计划加载失败: {res}']
            return
        self.plan_progress = []
        progresses = res.json()['data']['planOngoingProgress']
        for progress in progresses:
            plan = progress['plan']
            self.plan_progress.append(rumps.MenuItem(f"{plan['name']}" + f" ({progress['completedNum']}/{plan['days']})", self._do_nothing))
        
    
    def _req(self, data):
        with open("config.json") as f:
            j = json.load(f)
            self.headers['cookie'] = ";".join([f"{k}={j[k]}" for k in ("csrftoken", "LEETCODE_SESSION")])
        return requests.post(self.url, data=data, headers=self.headers)
    
    def _do_nothing(self, sender):
        pass


if __name__ == "__main__":
    app = LeetCodeStatusBarApp()
    app.run()
