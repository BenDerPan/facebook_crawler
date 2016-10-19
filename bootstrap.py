from chrome_api.fb import CrawlerThread
if __name__ == "__main__":
    fb_crawler_thread = CrawlerThread(1, "Thread-1")
    fb_crawler_thread.start()
    print('Exit main threading')