import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)


def add_subscription(subscription):
    subscription_manager.add_subscription(subscription)
    return "add success"


def remove_subscription(subscription):
    subscription_manager.remove_subscription(subscription)
    return "remove success"


def list_subscriptions():
    subscriptions = subscription_manager.list_subscriptions()
    df = pd.DataFrame(subscriptions, columns=["Subscriptions"])
    return df


def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

# 创建Gradio界面
export_report = gr.Interface(
    fn=export_progress_by_date_range,  # 指定界面调用的函数
    title="GitHubSentinel",  # 设置界面标题
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        ),  # 下拉菜单选择订阅的GitHub项目
        gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
        # 滑动条选择报告的时间范围
    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],  # 输出格式：Markdown文本和文件下载
)

with gr.Blocks() as maintain_subscriptions:
    name = gr.Textbox(label="Subscription")
    add_btn = gr.Button("Add")
    delete_btn = gr.Button("Delete")
    action_label = gr.Textbox("Action Result")
    search_btn = gr.Button("Search")
    pd_output = gr.Dataframe(headers=["Subscriptions",])
    add_btn.click(fn=add_subscription, inputs=name, outputs=action_label, api_name="add")
    delete_btn.click(fn=remove_subscription, inputs=name, outputs=action_label, api_name="remove")
    search_btn.click(fn=list_subscriptions, outputs=pd_output, api_name="search")

demo = gr.TabbedInterface([export_report, maintain_subscriptions], ["Generate Report", "Maintain Subscriptions"])

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
