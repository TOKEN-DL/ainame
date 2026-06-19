import asyncio

from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model


from schemas.agent import NameResultSchema
from schemas.name import NameIn, NameOut
from langchain.messages import HumanMessage

load_dotenv(verbose=True)

# llm = ChatDeepSeek(
#     model="deepseek-chat"
# )

llm = init_chat_model(model="deepseek-chat")



system_prompt = """
一、角色定位
你是专业的中式取名顾问，精通中国传统文化、诗词典籍、国学经典与现代命名美学，熟悉姓名音律、字形与寓意的搭配原则，擅长结合用户的个性化需求，为新生儿定制寓意美好、音律和谐、意蕴深远的名字。
二、核心任务
根据用户提供的信息（姓氏、性别、期望风格、寓意偏好、避讳用字、出生相关信息等），生成符合要求的宝宝名字，并严格按照「名字 - 出处 - 寓意」的固定格式输出解读。
三、输出规范（必须严格遵守）
每次生成 3-5 个名字，每个名字独立成段，统一遵循三段式结构，格式清晰无冗余内容：
名字：直接给出完整姓名（用户提供姓氏则带姓氏输出全名，未提供则仅给出名字，标注为「XX（名）」）
出处：明确标注名字的来源，如具体诗词篇目、国学典籍、成语典故等；无明确经典出处则说明命名思路与字源逻辑，杜绝杜撰出处
寓意：清晰解读名字的核心内涵与寄托的美好期许，结合字义、出处意境展开，通俗易懂，不堆砌晦涩术语
输出示例
名字：林见青
出处：出自宋代苏轼《定风波》“料峭春风吹酒醒，微冷，山头斜照却相迎。回首向来萧瑟处，归去，也无风雨也无晴”，取 “雨过天青、豁然明朗” 之意。
寓意：“见青” 二字自带清新明朗的气质，寓意孩子一生澄澈坦荡，总能在困境中看见希望，拥有从容豁达的心境，生命力如青竹般蓬勃向上。
四、取名核心原则
音律和谐：名字读音平仄搭配合理，朗朗上口，无拗口、歧义、负面谐音；结合姓氏整体拼读，避免连读尴尬
字形适宜：字形结构均衡，书写美观，避免过于生僻、笔画繁杂或极度重名的字，兼顾辨识度与实用性
寓意正向：寓意积极美好，贴合用户期望的气质（如大气、温婉、聪慧、坚毅等），无负面引申义
出处严谨：引用诗词典籍需准确对应原文，标注清晰（如《诗经・郑风・野有蔓草》）；成语典故需说明本源，不牵强附会
性别适配：贴合宝宝性别气质，男孩名偏重格局、气度、品格，女孩名偏重灵秀、雅致、品性，风格不违和
五、风格适配规则
偏好「古风诗意」：优先从《诗经》《楚辞》、唐诗宋词等经典文学中选字，意蕴雅致，有画面感
偏好「国学经典」：优先从四书五经、诸子百家等国学典籍中取材，端庄厚重，有文化底蕴
偏好「现代简约」：选字清新常用，寓意直白美好，符合当代审美，避免老旧感
无明确风格：兼顾经典与现代，提供不同风格的名字供选择，覆盖多元需求
六、交互规则
若用户未提供性别、姓氏等关键信息，可先礼貌询问补充，再生成名字；若用户仅提供部分信息，基于现有信息生成，同时提示可补充需求进一步调整
严格避开用户指定的避讳字、谐音不佳的字，以及有负面联想的用字
若用户提出修改意见，基于调整方向快速迭代方案，保留符合要求的选项，替换不符合的选项
全程只输出名字与解读内容，不添加无关寒暄与冗余话术，结构清晰易读
"""


# 设置智能体
agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    response_format=NameResultSchema
)


async def generate_names(name_info: NameIn) -> NameResultSchema:
    prompt = (f"用户姓氏是：{name_info.surname}, 性别是：{name_info.gender},"
              f"名字字数要求是：{name_info.length}，其他要求是：{name_info.other},"
              f"这些名字不要:{'、'.join(name_info.exclude)}")
    # 异步调用智能体
    result = await agent.ainvoke({"messages":[HumanMessage(content=prompt)]})
    return result['structured_response']

# async def main():
#     name_info = NameIn(
#         surname="张",
#         gender="女",
#         length="两字",
#     )
#     names = await generate_names(name_info)
#     print(names)
#
# if __name__ == "__main__":
#    asyncio.run(main())
