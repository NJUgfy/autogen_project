from agent_manager import AgentManager
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.search_agent import SearchAgent

def main():
    manager = AgentManager()
    planner = PlannerAgent()
    coder = CoderAgent()
    evaluator = EvaluatorAgent()
    searcher = SearchAgent()

    manager.add_agent(planner)
    manager.add_agent(coder)
    manager.add_agent(evaluator)
    manager.add_agent(searcher)

    initial_goal = """请生成一个arxivcs Daily网页，核心功能:
            1.需要存储论文数据，比如存储在data.js文件中, 至少5条以上, 其中分类请用缩写,例如cs_AI, 其中id请用pdf_url的后缀, 例如https://arxiv.org/pdf/2405.12345.pdf中使用2405.12345作为id, 并且前端代码需要引用这个数据文件来展示数据。
            2.script.js文件:负责加载并渲染data.js中的数据，其他html文件会引用script.js中的方法;
            3.一个首页比如index.html，有论文列表， 其中列出arxiv核心CS分类，点击具体分类后会带上参数,例如?cat=cs_AI以跳转到category.html页面, 实现筛选论文列表的功能;
            4.category.html页面:按时间倒序排列论文列表，其中论文列表数据来自data.js，需要引用data.js，并且根据传入的?cat参数，来筛选data.js中的论文;
            5.在category.html点击具体论文后，会跳转到论文详情页,名称例如detail.html, 需要实现有效的跳转;
            6.论文详情页detail.html:包含PDF链接、作者、提交日期、BibTeX引用，支持一键复制, 这里论文的数据也是来自于data.js文件的数据。
        代码要求:
            - HTML:结构完整(包含doctype、html、head、body标盗)，引入必要的cs5/J5文件;
            - css:样式简洁美观，适配浏览器默认尺寸，css代码文件内只能包含c5S代码，
            - Js:语法规范，添加必要注释，避免报错;
            - 所有文件需相互兼容(如script.js中的函数名不冲突，html中的链接路径正确)
            - 前端html代码中如果引用外部js文件，请保证引用数据的字段名称和js 文件中定义的一致。
            - 对论文数据的字段在不同文件要保持一致，比如分类字段要统一叫category，pdf链接统一叫pdf_url等。
            - 对data.js文件中的论文数据，至少包含以下字段并且在其他引用到data.js的文件中统一字段格式:id,title,authors,abstract,pdf_url,submitted,category, bibtex
        The entire project should be in an "output/arxiv_cs_daily' directory.
    """
    
    print("\nStarting multi-agent workflow...")
    manager.start_task(initial_goal, planner.name)

if __name__ == "__main__":
    main()
