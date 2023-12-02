

SITES_SETTINGS = {'freelance.habr.com': {'url': 'https://freelance.habr.com/tasks',
                                         'downloader': StaticDownloader,
                                         'parser': HabrParser},
                  'www.fl.ru': {'url': 'ttps://www.fl.ru/projects/',
                                'downloader': StaticDownloader,
                                'parser': FLParser},
                  'youdo.com': {'url': 'https://youdo.com/tasks-all-opened-all',
                                'downloader': DynamicDownloader,
                                'parser': YouDoParser}
                  }