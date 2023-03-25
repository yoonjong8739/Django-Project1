import tweepy
import pandas as pd
import datetime as dt
from dateutil.tz import gettz
try:
    import mysecrets
except:
    pass


class TwitterCrawler:

    def __init__(self, consumer_key, consumer_secret):
        self.auth = tweepy.OAuth1UserHandler(consumer_key=consumer_key,
                                             consumer_secret=consumer_secret)
        self.api = tweepy.API(self.auth)
        self.korea_geo = "%s,%s,%s" % ("35.95", "128.25", "1000km")

    def fetch_tweets(self, q, count):
        statuses = self.api.search_tweets(q=q, geocode=self.korea_geo, count=count)
        return statuses

    @staticmethod
    def get_values_from_statuses(statuses, title, params: list):
        num = len(statuses)
        if num ==0:
            return None

        value_list = []

        for i in range(num):
            status = statuses[i]
            ori_dict = {'title': title}
            # values = {param: getattr(status, param).replace("\n", " ") if param != 'created_at' else getattr(status, param).strftime('%Y-%m-%d') for param in params}
            values = {param: getattr(status, param) for param in params}
            values['created_at'] = values['created_at'].strftime('%Y-%m-%d')
            values['text'] = values['text'].replace("\n", " ")
            ori_dict.update(values)
            value_list.append(ori_dict)

        return value_list

    @staticmethod
    def export_to_csv(in_list, outfile):
        df = pd.DataFrame.from_records(in_list)
        today = dt.datetime.now(gettz('Asia/Seoul')).today().strftime('%Y-%m-%d')
        df['date'] = today
        df.to_csv(f'../outfile/rank/trending_{today}/{outfile}_{today}.csv', mode='w', index=False, header=True, encoding='utf-8-sig')
        print(outfile+' is saved')

    def run_crawler(self, to_search: list, keywords: list) -> None:
        twit_list = []

        for keyword in keywords:
            q = f'"{keyword}"'
            statuses = self.fetch_tweets(q, 100)
            rst_list = self.get_values_from_statuses(statuses, keyword, to_search)

            if rst_list:
                for item in rst_list:
                    twit_list.append(item)

        self.export_to_csv(twit_list, 'weekly_tweets')




# if __name__ == '__main__':
#
#     twitter_crawler = TwitterCrawler(mysecrets.consumer_key, mysecrets.consumer_secret)
#     search_list = ['created_at', 'text', 'retweet_count', 'favorite_count']
#     keyword_list = ['구의 증명', '사라진 여자들', '김미경의 마흔 수업']
#     twitter_crawler.run_crawler(search_list, keyword_list)
