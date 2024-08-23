from langchain.chains.llm import LLMChain
from langchain_community.llms.chatglm import ChatGLM
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

from dotenv import load_dotenv

load_dotenv()


class LLM:
    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = True):
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")

        # 翻译任务指令始终由 System 角色承担
        template = (
            "You are a technical expert, and proficient in Github and project management. \n"
            "The following is the latest progress of the project. Please merge similar items according to their functions to form a brief report, which at least includes: 1) New features; 2) Major improvements; 3) Fixed issues;\n"
            "The final result should be in markdown format in {target_language}. "
        )

        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        # 待总结文本由 Human 角色输入
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        if model_name == "gpt-3.5-turbo" or model_name == "gpt-4o-mini":
            # 为了翻译结果的稳定性，将 temperature 设置为 0
            chat = ChatOpenAI(model_name=model_name, temperature=0, verbose=verbose)
        elif model_name == "chat_glm":
            endpoint_url = ("http://127.0.0.1:8000")  # endpoint_url 填写跑模型的地址
            chat = ChatGLM(endpoint_url=endpoint_url, temperature=0, verbose=verbose)
        else:
            raise Exception(f"This model is not supported. ModelName:{model_name}")

        self.chain = LLMChain(llm=chat, prompt=chat_prompt_template, verbose=verbose)

    def generate_daily_report(self, markdown_content, target_language: str = "Chinese", dry_run=False):
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        result = ""
        try:
            result = self.chain.run({
                "text": markdown_content,
                "target_language": target_language,
            })

            LOG.debug(result)
            return result
        except Exception as e:
            LOG.error(f"An error occurred while generating the report: {e}")
            return result
