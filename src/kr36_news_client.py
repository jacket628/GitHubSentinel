import requests  # 导入requests库用于HTTP请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库用于解析HTML内容
from datetime import datetime, timedelta  # 导入datetime模块用于获取日期和时间
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class Kr36NewsClient:
    def __init__(self):
        self.url = 'https://36kr.com/information/AI/'  # 36kr的URL

    def export_top_articles(self):
        LOG.debug("准备获取Hacker News的热门新闻。")
        try:
            # 获取今天的日期并格式化
            today_date = datetime.now().strftime("%Y%m%d")
            two_days_ago = datetime.now() - timedelta(days=2)

            # 发送HTTP请求
            response = requests.get(self.url, timeout=10)
            html_content = response.content

            # 使用BeautifulSoup解析网页内容
            soup = BeautifulSoup(html_content, 'html.parser')

            # 找到新闻列表部分，使用 'kr-flow-article-item' 作为选择器
            articles = soup.find_all('div', class_='kr-flow-article-item')

            # 创建Markdown格式的内容
            markdown_content = "# 36kr AI 新闻列表\n\n"

            for article in articles:
                # 获取新闻标题
                title_tag = article.find('a', class_='article-item-title')
                title = title_tag.text.strip() if title_tag else "无标题"

                # 获取摘要
                summary_tag = article.find('a', class_='article-item-description')
                summary = summary_tag.text.strip() if summary_tag else "无摘要"

                # 获取发布来源
                source_tag = article.find('a', class_='kr-flow-bar-author')
                source = source_tag.text.strip() if source_tag else "未知来源"

                # 获取发布时间
                publish_time_tag = article.find('span', class_='kr-flow-bar-time')
                publish_time = publish_time_tag.text.strip() if publish_time_tag else "未知时间"

                # 获取详情页链接
                link_tag = article.find('a', class_='article-item-title')
                link = f"https://36kr.com{link_tag['href']}" if link_tag else "无链接"

                # 解析发布时间
                # if "小时前" in publish_time:
                #     # 如果是 X小时前的格式
                #     hours_ago = int(publish_time.replace("小时前", "").strip())
                #     publish_time_datetime = datetime.now() - timedelta(hours=hours_ago)
                # elif "天前" in publish_time:
                #     # 如果是 X天前的格式
                #     days_ago = int(publish_time.replace("天前", "").strip())
                #     publish_time_datetime = datetime.now() - timedelta(days=days_ago)
                # else:
                #     # 如果是其他日期格式，如 '2024-09-06'
                #     try:
                #         publish_time_datetime = datetime.strptime(publish_time, '%Y-%m-%d')
                #     except ValueError:
                #         publish_time_datetime = datetime.now()  # 默认当前时间

                # # 检查是否超过2天，如果超过则跳过
                # if publish_time_datetime < two_days_ago:
                #     continue

                # 组装Markdown内容
                markdown_content += f"## [{title}]({link})\n\n"
                markdown_content += f"- **摘要**: {summary}\n"
                markdown_content += f"- **来源**: {source}\n"
                markdown_content += f"- **发布时间**: {publish_time}\n"
                markdown_content += f"- **详情页**: [点击查看]({link})\n\n"

            # 构建存储路径
            dir_path = 'kr36_news'
            os.makedirs(dir_path, exist_ok=True)  # 确保目录存在
            file_path = os.path.join(dir_path, f'{today_date}.md')  # 定义文件路径

            # 导出Markdown文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(markdown_content)

            LOG.info(f"36kr AI的最近新闻文件生成：{file_path}")
            return file_path
        except Exception as e:
            LOG.error(f"获取36kr AI的最近新闻失败：{str(e)}")
            return []


if __name__ == "__main__":
    client = Kr36NewsClient()
    client.export_top_articles()  # 默认情况下使用当前日期和时间
