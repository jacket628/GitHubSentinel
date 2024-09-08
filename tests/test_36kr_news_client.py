import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import datetime
from kr36_news_client import Kr36NewsClient

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestKr36NewsClient(unittest.TestCase):
    def setUp(self):
        self.client = Kr36NewsClient()

    @patch('requests.get')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_export_top_articles_success(self, mock_open, mock_makedirs, mock_requests_get):
        # 设置模拟的HTTP响应内容
        mock_response = MagicMock()
        mock_response.content = '''
        <html>
            <body>
                <div class="kr-flow-article-item">
                    <a class="article-item-title" href="/article1">Article 1</a>
                    <a class="article-item-description">This is the first article</a>
                    <a class="kr-flow-bar-author">Author 1</a>
                    <span class="kr-flow-bar-time">2小时前</span>
                </div>
                <div class="kr-flow-article-item">
                    <a class="article-item-title" href="/article2">Article 2</a>
                    <a class="article-item-description">This is the second article</a>
                    <a class="kr-flow-bar-author">Author 2</a>
                    <span class="kr-flow-bar-time">1天前</span>
                </div>
            </body>
        </html>
        '''
        mock_requests_get.return_value = mock_response

        result = self.client.export_top_articles()

        # 检查创建目录的调用
        mock_makedirs.assert_called_once_with('36kr_news', exist_ok=True)

        # 检查写入文件的调用
        mock_open.assert_called_once()
        mock_open().write.assert_called_once()

        # 检查文件路径
        dir_path = '36kr_news'
        today_date = datetime.now().strftime("%Y%m%d")
        expected_file_path = os.path.join(dir_path, f'{dir_path}_{today_date}.md')
        self.assertIn(expected_file_path, result, "文件路径不匹配")

    @patch('requests.get')
    def test_export_top_articles_failure(self, mock_requests_get):
        # 模拟请求失败
        mock_requests_get.side_effect = Exception("请求失败")

        result = self.client.export_top_articles()

        # 检查返回值
        self.assertEqual(result, [], "当请求失败时，应该返回空列表")

    @patch('requests.get')
    def test_export_top_articles_no_articles(self, mock_requests_get):
        # 设置没有文章的HTML内容
        mock_response = MagicMock()
        mock_response.content = '''
        <html>
            <body>
                <div>No articles found</div>
            </body>
        </html>
        '''
        mock_requests_get.return_value = mock_response
        result = self.client.export_top_articles()

        # 确保生成的Markdown内容没有文章
        self.assertNotIn("# 36kr AI 新闻列表\n\n", result)


if __name__ == '__main__':
    unittest.main()
