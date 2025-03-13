#from bot_forge import BotForge
from botforge import bot_forge
from bot_forge.tool_usage import ToolUsage
from bot_forge.bot_forge_beta import ToolDirectReturnError
import threading
import time
from loguru import logger
# BotForge token，目前测试无需配置Token。后续正式版本，直接页面注册即可获得
# BotForge token, no need to configure during beta test. Need to apply from BotForge page when officially released
BOT_FORGE_TOKEN = '*'

# 修改为你使用的飞书机器人的APP_ID和APP_SECRET, 需要从飞书应用的后台获得
# APP_ID and APP_SECRET of Feishu bot, need to get from Feishu Open Platform
BOT_APP_ID = 'cli_a5d6c0ea947c100c'
BOT_APP_SECRET = "GXiODcYKvc8fVr5KrNkQMhFbBFId7OLT"

# GPT智能体的名字，每个智能体需要唯一
# Bot agent name, need to be unique
BOT_AGENT_NAME = 'SPA-GPT-TEST'

# 本地工具服务的内网公开名字，每个工具服务器需要唯一，这个复用智能体名字
# Local tool service name, need to be unique, reuse the agent name here
TOOL_SERVICE_NAME = BOT_AGENT_NAME

# 文档集注册名字，每个文档集需要唯一，这个复用智能体名字
# Document collection name, need to be unique, reuse the agent name here
DOCUMENT_COLLECTION_NAME = BOT_AGENT_NAME

sub_agent_name = 'ANALYSIS-AGENT'
# 示例工具1：无参函数，返回值需要类型注释
# Example tool 1: function without parameters, return value needs type hint
def about_me() -> str:
    """
    Returns information about myself.

    This function provides a detailed string describing who I am, what I can do,
    and how users can interact with me. It covers my functional capabilities such as
    MSF diagnosis, debugging assistance, offline analysis, and knowledge question-and-answer, etc.

    Returns:
        str: A string that describes my functionalities and how to interact with me.

    Note:
        Do not omit any part of the returned information. Ensure content is complete and well-formatted
        before replying directly to the user.
    """
    about_info = '''我是一个自动驾驶行业软件开发专家，我主要负责车身和传感器信号的抽象，
    我能帮助分析信号映射， 自动生成总线测试信号值以及预期输出结果值
    '''
    raise ToolDirectReturnError(about_info)

def get_what_year() -> str:
    """Returns what year is it."""
    return 'It is 2199'
def sub_analysis_case(caseid:str,chat_context: dict,type:str= 'default_type',) -> str:
    logger.info(chat_context)
    user_id = chat_context['user_id']
    all_str = f'基本信息{chat_context},caseid:{caseid},type:{type}'
    logger.info(all_str)
    agent_result = bot_forge.agent_invoke(sub_agent_name,sub_agent_name,all_str)
    print(agent_result)
    logger.info(agent_result)
    content = ToolUsage.to_rich_text(at=[chat_context['user_id']], title="分析结果", text={1: agent_result})
    logger.info(content)
    bot_forge.update_message(chat_context['reply_message_id'],content=content, msg_type='post')

def analysis_case(caseid:str,type:str= 'default_type') -> str:
    """根据用户输入的网址提取出caseid,通过caseid查询case信息
    args:
        caseid (str): 用户网址中details后面的数字为caseid，长度为10位 如果没有caseid则返回错误信息
        type (str): 默认为default_type
    Returns:
        str: 分析结果
    """
    context_str = bot_forge.get_chat_context()
    logger.info(context_str)

    thread = threading.Thread(target=sub_analysis_case,
                               args=(caseid, bot_forge.get_chat_context(),type))
    thread.start()
    return_info = f'你好 当前caseid为{caseid}的已经收到，我们会尽快处理，结果请关注后续消息'
    raise ToolDirectReturnError(return_info)

prompt_all = '''你是自动驾驶行业软件开发专家，你主要负责车身和传感器信号的抽象
'''

sub_agent_prompt = '''你是自动驾驶行业软件开发专家，你主要负责车身和传感器信号的抽象，
请根据我提供的原始信号和中间件信号的对应关系, 帮我设计3组测试值, 我提供的signal mapping中$0代表输出信号,$1-$x代表输入信号
请将你的所有设计测试值以及预期输出结果值用json返回给我,JSON的key都是用我提供的映射关系表中的描述方式
返回值:合法的JSON字符串,可以用python json.loads() 校验
示例:
{
    "msf_input": {
        "xxxxx.dfdf.dfdf": [1,0,1],
        "yyyyyyyyy.dsfsf.sdfdsf": [1,0,1]
    },
    "msf_output": {
        "zzzzzzz.dfdf.dfdf.dfd": [1,0,1],
        "dddfd.dfdfd.saada.dfsd": [2,1,2]
    }
}
要求:
1. 不要在结果中包含任何其他字符,比如markdown ```json ```
2. 测试值只能是浮点数， 比如true用1,false用0, None用0
3. 如果我给你msf_input是空字符串, 就只尝试构造输出信号的期望值
4. 不能推导出每个输出信号的具体输出数值，就不要构造测试和输出
5. 你给我的msf_input和msf_output中的所有信号描述,个数和顺序上都必须和我给你的完全对齐。
'''
def main():
    # 初始化BotForge，目前测试无需配置Token
    # BotForge token, no need to configure during beta test
    #bot_forge = BotForge(token='*')

    # 注册本地工具服务
    # Register local tool service
    bot_forge.register_tools(
        service_name=TOOL_SERVICE_NAME,
        tool_funcs=[about_me,analysis_case]
    )

    # 注册智能体
    # Register agent
    bot_forge.register_agent(
        name=BOT_AGENT_NAME,
        prompt= prompt_all,
        tools=[
            # 工具配置项：
            #   0: 是工具服务名字
            #   1: 是工具名字，`*`表示该服务下所有工具
            #   2: 是该工具是否必须
            # tool config item:
            #   first is tool service name
            #   second is the tool name and `*` means all tools in this service
            #   third is whether this tool is required  #
            (TOOL_SERVICE_NAME, '*', True),
            # ...
        ],
        agents=[
            # 智能体递归支持：
            #  0: 子智能体名字
            #  1: 子智能体具备的功能介绍
            # agent recursive support:
            #  0: sub-agent name
            #  1: sub-agent capabilities
            #(sub_agent_name, sub_agent_prompt),
        ],
        # 配置GPT模型，不配置默认是gpt-35-turbo(快)，可以按需切换gpt-4(聪明)
        # Configure GPT model, default to gpt-35-turbo (fast), can switch to gpt-4 (smart) as needed
        kwargs={
            'deployment_name': 'gpt-4',
            'model_name': 'gpt-4o'
        }
    )
    bot_forge.register_agent(
        name=sub_agent_name,
        prompt= sub_agent_prompt,
        agents=[
            # 智能体递归支持：
            #  0: 子智能体名字
            #  1: 子智能体具备的功能介绍
            # agent recursive support:
            #  0: sub-agent name
            #  1: sub-agent capabilities
            #(sub_agent_name, sub_agent_prompt),
        ],
        # 配置GPT模型，不配置默认是gpt-35-turbo(快)，可以按需切换gpt-4(聪明)
        # Configure GPT model, default to gpt-35-turbo (fast), can switch to gpt-4 (smart) as needed
        kwargs={
            'deployment_name': 'gpt-4',
            'model_name': 'gpt-4o',
            'max_history_length':0
        }
    )
    # 注册机器人
    # Register bot
    bot_forge.register_bot(
        app_id=BOT_APP_ID,
        app_secret=BOT_APP_SECRET,
        bind_agent=BOT_AGENT_NAME,
        # respond_to_all: 配置是否响应@所有人的消息，默认为True，即响应
        # respond_to_all config whether to respond to @all messages, default is True, which means respond
        # respond_to_all=False,
        # bind_chat_id: 配置机器人绑定的群ID，不配置则默认为绑定所有群
        bind_chat_id='oc_44fa84154b88737e3827f674deb704e4',
    )

    # 启动机器人工坊
    # Start BotForge
    bot_forge.run()

def agent_run():
    agent_thread = threading.Thread(target=main)
    agent_thread.daemon = True
    agent_thread.start()
    time.sleep(5)
    return
