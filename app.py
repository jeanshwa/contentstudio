import streamlit as st
import json
import re
from datetime import datetime

# ─── Page config ───
st.set_page_config(
    page_title="内容工厂 | Legal Content Studio",
    page_icon="⚖️",
    layout="centered",
)

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap');
.stApp { font-family: 'Noto Sans SC', sans-serif; }
.app-header {
    background: linear-gradient(135deg, #d4380d 0%, #ff6b35 100%);
    color: white; padding: 1.5rem 1.2rem; border-radius: 16px;
    margin-bottom: 1.5rem; text-align: center;
}
.app-header h1 { font-size: 1.6rem; font-weight: 900; margin: 0 0 0.3rem 0; }
.app-header p { font-size: 0.85rem; opacity: 0.9; margin: 0; }
.content-card {
    background: #fffbf5; border: 1px solid #ffe0cc; border-radius: 14px;
    padding: 1.2rem; margin: 1rem 0; line-height: 1.85; font-size: 0.95rem;
    white-space: pre-wrap; word-wrap: break-word;
}
.news-card {
    background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 14px;
    padding: 1.2rem; margin: 1rem 0; font-size: 0.88rem; line-height: 1.7;
}
.news-card h4 { color: #389e0d; margin: 0 0 0.5rem 0; font-size: 0.95rem; }
.platform-tag {
    display: inline-block; padding: 0.25rem 0.7rem; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; margin-bottom: 0.5rem;
}
.tag-xhs { background: #ff2442; color: white; }
.tag-wechat { background: #07c160; color: white; }
.section-label {
    font-size: 0.8rem; font-weight: 600; color: #8c8c8c;
    text-transform: uppercase; letter-spacing: 1px; margin: 1.5rem 0 0.5rem 0;
}
.fancy-divider { text-align: center; margin: 2rem 0; color: #d9d9d9; font-size: 0.8rem; letter-spacing: 4px; }
.model-badge {
    display: inline-block; padding: 0.2rem 0.6rem; border-radius: 8px;
    font-size: 0.7rem; font-weight: 700; color: white; margin-left: 0.3rem;
}
.badge-claude { background: #d4380d; }
.badge-gemini { background: #4285f4; }
.badge-grok { background: #000000; }
@media (max-width: 768px) {
    .stApp { padding: 0.2rem; }
    .content-card { font-size: 0.92rem; padding: 1rem; }
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stButton > button { border-radius: 10px; font-weight: 600; padding: 0.5rem 1rem; }
</style>
""", unsafe_allow_html=True)

# ─── Password Gate ───
try:
    APP_PASSWORD = st.secrets.get("APP_PASSWORD", "hello1234")
except Exception:
    APP_PASSWORD = "hello1234"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="app-header">
        <h1>⚖️ 内容工厂</h1>
        <p>请输入密码登录</p>
    </div>
    """, unsafe_allow_html=True)

    pwd = st.text_input("🔒 密码 Password", type="password", placeholder="请输入密码...")
    if st.button("登录 Login", use_container_width=True, type="primary"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 密码错误，请重试")
    st.stop()

# ─── Header ───
st.markdown("""
<div class="app-header">
    <h1>⚖️ 内容工厂</h1>
    <p>一键抓取新闻 → AI生成爆款帖 → 复制粘贴发布</p>
</div>
""", unsafe_allow_html=True)

# ─── Model configs ───
MODELS = {
    "Claude (Anthropic)": {
        "badge": "badge-claude",
        "secret_key": "ANTHROPIC_API_KEY",
        "help": "console.anthropic.com 获取",
    },
    "Gemini (Google)": {
        "badge": "badge-gemini",
        "secret_key": "GOOGLE_API_KEY",
        "help": "aistudio.google.com/apikey 获取",
    },
    "Grok (xAI)": {
        "badge": "badge-grok",
        "secret_key": "XAI_API_KEY",
        "help": "console.x.ai 获取",
    },
}

# ─── Sidebar ───
with st.sidebar:
    st.markdown("### ⚙️ 设置 Settings")

    selected_model = st.selectbox("🤖 选择AI模型", options=list(MODELS.keys()))
    model_cfg = MODELS[selected_model]

    api_key = st.text_input(
        f"{selected_model} API Key",
        type="password",
        help=model_cfg["help"],
        key="api_key_input",
    )

    # Resolve API key: input > secrets
    resolved_key = api_key
    if not resolved_key:
        try:
            resolved_key = st.secrets.get(model_cfg["secret_key"], "")
        except Exception:
            pass

    if resolved_key:
        st.success(f"✅ {selected_model} Key 已就绪")
    else:
        st.warning(f"请输入 {selected_model} API Key")

    st.markdown("---")
    st.markdown("""
    **使用方法：**
    1. 选AI模型 + 输入API Key
    2. 选话题 → 抓取新闻
    3. 生成帖子 → 复制粘贴
    """)
    st.markdown("---")
    st.caption("Built for Sydney conveyancing & property solicitors 🇦🇺")


# ─── Topics ───
TOPICS = {
    "🏠 房产过户 Conveyancing": {
        "queries": [
            "Australia property conveyancing law changes 2026",
            "NSW stamp duty update news",
            "Sydney property settlement news",
        ],
        "angle": "房产过户、印花税、产权转让",
    },
    "📈 房市动态 Property Market": {
        "queries": [
            "Sydney property market news today",
            "Australia housing prices forecast 2026",
            "NSW property auction results",
        ],
        "angle": "悉尼房价走势、拍卖结果、市场预测",
    },
    "📜 遗嘱遗产 Wills & Estates": {
        "queries": [
            "Australia wills estate planning law news",
            "NSW probate inheritance dispute news",
            "Australia succession law update",
        ],
        "angle": "遗嘱规划、遗产分配、继承纠纷",
    },
    "🏗️ 信托架构 Trust Structures": {
        "queries": [
            "Australia family trust tax structure news 2026",
            "discretionary trust Australia tax update",
            "Australia property trust structure news",
        ],
        "angle": "家族信托、税务规划、资产保护架构",
    },
    "🌏 移民签证 Immigration": {
        "queries": [
            "Australia immigration visa policy update 2026",
            "Australia skilled visa news",
            "Australia investor visa property news",
        ],
        "angle": "签证政策变化、移民与购房、投资移民",
    },
}

st.markdown('<div class="section-label">📌 选择话题 Choose Topic</div>', unsafe_allow_html=True)
selected_topic = st.selectbox("话题分类", options=list(TOPICS.keys()), label_visibility="collapsed")

# ═══════════════════════════════════════
# API CLIENTS
# ═══════════════════════════════════════

def require_key():
    if not resolved_key:
        st.error(f"⚠️ 请输入 {selected_model} 的 API Key")
        st.stop()
    return resolved_key


# ─── Claude (Anthropic) ───
def claude_fetch_news(key, topic_cfg):
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    queries_text = "\n".join(f"- {q}" for q in topic_cfg["queries"])
    prompt = _news_prompt(queries_text)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    full_text = ""
    for block in (response.content or []):
        if hasattr(block, "text"):
            full_text += block.text
    if not full_text:
        raise ValueError("Claude 返回内容为空，请重试")
    return _parse_news_json(full_text)


def claude_generate_post(key, news_data, topic_cfg, platform):
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    prompt = _post_prompt(news_data, topic_cfg, platform)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ─── Gemini (Google) ───
def gemini_fetch_news(key, topic_cfg):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    queries_text = "\n".join(f"- {q}" for q in topic_cfg["queries"])
    prompt = _news_prompt(queries_text)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    text = response.text or ""
    if not text:
        raise ValueError("Gemini 返回内容为空，请重试")
    return _parse_news_json(text)


def gemini_generate_post(key, news_data, topic_cfg, platform):
    from google import genai
    client = genai.Client(api_key=key)
    prompt = _post_prompt(news_data, topic_cfg, platform)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


# ─── Grok (xAI) ───
def grok_fetch_news(key, topic_cfg):
    from openai import OpenAI
    client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
    queries_text = "\n".join(f"- {q}" for q in topic_cfg["queries"])
    prompt = _news_prompt(queries_text)
    try:
        response = client.responses.create(
            model="grok-3-mini-fast",
            input=[{"role": "user", "content": prompt}],
            tools=[{"type": "web_search"}],
        )
        full_text = ""
        output = response.output or []
        for block in output:
            if hasattr(block, "content") and block.content:
                for part in block.content:
                    if hasattr(part, "text"):
                        full_text += part.text
            elif hasattr(block, "text"):
                full_text += block.text
        if not full_text:
            full_text = str(response)
        return _parse_news_json(full_text)
    except Exception:
        # Fallback: use chat completions without search
        response = client.chat.completions.create(
            model="grok-3-mini-fast",
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_news_json(response.choices[0].message.content)


def grok_generate_post(key, news_data, topic_cfg, platform):
    from openai import OpenAI
    client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
    prompt = _post_prompt(news_data, topic_cfg, platform)
    response = client.chat.completions.create(
        model="grok-3-mini-fast",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ═══════════════════════════════════════
# SHARED PROMPTS & UTILS
# ═══════════════════════════════════════

def _news_prompt(queries_text):
    return f"""You are a research assistant for a Sydney-based solicitor who specialises in conveyancing, property, wills, estates and trust structures, serving Chinese-speaking clients in Australia.

Search the web for the latest news on these topics:
{queries_text}

Return a JSON object (no markdown fences) with this structure:
{{
  "articles": [
    {{
      "headline": "English headline",
      "headline_cn": "中文标题",
      "summary": "2-3 sentence English summary of the key facts",
      "summary_cn": "2-3句中文摘要",
      "source": "source name",
      "relevance": "Why this matters for Chinese-speaking property buyers/families in Sydney"
    }}
  ]
}}

Find 3-5 of the most recent and relevant articles. Today's date is {datetime.now().strftime('%d %B %Y')}.
Focus on news from the last 2 weeks. If you can't find very recent news, get the most recent available.
Return ONLY the JSON object, nothing else."""


def _post_prompt(news_data, topic_cfg, platform):
    news_summary = json.dumps(news_data, ensure_ascii=False, indent=2)
    platform_instructions = {
        "小红书": """写一篇小红书风格的帖子。要求：
- 标题要有emoji，吸引眼球，用「」括起关键词
- 开头用一个幽默的小故事或段子引入话题（比如客户的搞笑经历、生活中的趣事类比）
- 语气亲切接地气，像朋友聊天，可以用"姐妹们"、"兄弟们"、"宝子们"开头
- 适当用emoji装饰但不要过度
- 中间穿插干货知识点，用简短的分点
- 结尾要有互动引导（点赞收藏评论）
- 最后加上 5-8 个相关hashtag标签
- 加上「📍悉尼 · 专业律师在线解答」
- 字数控制在 300-500 字
- 结尾引导私信咨询""",
        "微信": """写一篇微信公众号/朋友圈风格的帖子。要求：
- 标题专业但有趣，引发好奇心
- 开头用一个生动的故事或案例引入（可以虚构一个典型场景，加入幽默元素）
- 语气专业但不死板，偶尔来点幽默调侃
- 内容有深度，展示专业知识
- 段落分明，适合手机阅读
- 结尾有明确的行动号召
- 字数控制在 400-600 字
- 底部加联系方式引导""",
    }
    return f"""你是一位在悉尼执业的华人律师，专精房产过户(conveyancing)、物业法、遗嘱遗产和信托架构。
你的目标读者是澳洲的华人社区。你的写作风格幽默风趣，善于用生活化的比喻和小故事来解释复杂的法律概念。

以下是最新抓取的相关新闻资讯：
{news_summary}

话题方向：{topic_cfg['angle']}

{platform_instructions[platform]}

重要提示：
1. 一定要加入幽默故事元素！可以是：
   - 一个虚构但真实感十足的客户故事（"上周有个客户来找我..."）
   - 把法律概念用做菜、打游戏、谈恋爱来类比
   - 自嘲律师生活的段子
2. 内容要基于上面的真实新闻，但用轻松的方式传达
3. 确保法律信息准确，但表达要接地气
4. 不要编造具体的法律条文数字，如果不确定就用"根据最新政策"这类表述

直接输出帖子内容，不要加任何前言或解释。"""


def _parse_news_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"articles": [], "raw": text}


# ─── Dispatch table ───
DISPATCH = {
    "Claude (Anthropic)": {"fetch": claude_fetch_news, "generate": claude_generate_post},
    "Gemini (Google)":    {"fetch": gemini_fetch_news, "generate": gemini_generate_post},
    "Grok (xAI)":        {"fetch": grok_fetch_news,   "generate": grok_generate_post},
}


# ═══════════════════════════════════════
# MAIN FLOW
# ═══════════════════════════════════════

if "news_data" not in st.session_state:
    st.session_state.news_data = None
if "posts" not in st.session_state:
    st.session_state.posts = {}

badge_cls = model_cfg["badge"]
st.markdown(
    f'<div class="section-label">🔍 第一步：抓取新闻 <span class="model-badge {badge_cls}">{selected_model.split(" ")[0]}</span></div>',
    unsafe_allow_html=True,
)

if st.button("🔍 抓取最新新闻", use_container_width=True, type="primary"):
    key = require_key()
    topic_cfg = TOPICS[selected_topic]
    fetch_fn = DISPATCH[selected_model]["fetch"]
    with st.spinner(f"🌐 {selected_model} 正在搜索最新新闻..."):
        try:
            news = fetch_fn(key, topic_cfg)
            st.session_state.news_data = news
            st.session_state.posts = {}
        except Exception as e:
            st.error(f"抓取失败: {e}")

# Display news
if st.session_state.news_data:
    articles = st.session_state.news_data.get("articles", [])
    if articles:
        st.markdown(f'<div class="news-card"><h4>📰 找到 {len(articles)} 条相关新闻</h4>', unsafe_allow_html=True)
        for i, article in enumerate(articles):
            hl = article.get("headline_cn", article.get("headline", ""))
            summary = article.get("summary_cn", article.get("summary", ""))
            source = article.get("source", "")
            st.markdown(f"**{i+1}. {hl}**")
            st.markdown(f"{summary}")
            if source:
                st.caption(f"来源: {source}")
            if i < len(articles) - 1:
                st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        raw = st.session_state.news_data.get("raw", "")
        if raw:
            st.info("获取到资讯但格式解析有误，已显示原始内容：")
            st.text(raw)
        else:
            st.warning("未找到相关新闻，请尝试其他话题")

    # Step 2: Generate Posts
    st.markdown('<div class="fancy-divider">· · · · ·</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-label">✍️ 第二步：生成帖子 <span class="model-badge {badge_cls}">{selected_model.split(" ")[0]}</span></div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        gen_xhs = st.button("📕 生成小红书帖", use_container_width=True, type="primary")
    with col2:
        gen_wx = st.button("💬 生成微信帖", use_container_width=True)

    if gen_xhs or gen_wx:
        key = require_key()
        topic_cfg = TOPICS[selected_topic]
        platform = "小红书" if gen_xhs else "微信"
        gen_fn = DISPATCH[selected_model]["generate"]
        with st.spinner(f"✨ {selected_model} 正在创作{platform}帖子..."):
            try:
                post = gen_fn(key, st.session_state.news_data, topic_cfg, platform)
                st.session_state.posts[platform] = post
            except Exception as e:
                st.error(f"生成失败: {e}")

    # Display posts
    for platform, post in st.session_state.posts.items():
        st.markdown('<div class="fancy-divider">· · · · ·</div>', unsafe_allow_html=True)
        tag_class = "tag-xhs" if platform == "小红书" else "tag-wechat"
        icon = "📕" if platform == "小红书" else "💬"
        st.markdown(f'<span class="platform-tag {tag_class}">{icon} {platform}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="content-card">{post}</div>', unsafe_allow_html=True)

        with st.expander(f"📋 点击复制 {platform} 内容", expanded=False):
            st.text_area(
                "长按全选复制 (Long press to select & copy)",
                value=post, height=300, key=f"copy_{platform}",
            )

        if st.button(f"🔄 重新生成 {platform}", key=f"regen_{platform}"):
            key = require_key()
            topic_cfg = TOPICS[selected_topic]
            gen_fn = DISPATCH[selected_model]["generate"]
            with st.spinner("✨ 重新创作中..."):
                try:
                    st.session_state.posts[platform] = gen_fn(key, st.session_state.news_data, topic_cfg, platform)
                    st.rerun()
                except Exception as e:
                    st.error(f"生成失败: {e}")

# Footer
st.markdown('<div class="fancy-divider">· · · · ·</div>', unsafe_allow_html=True)
st.caption("⚖️ 内容工厂 v2.0 — 支持 Claude / Gemini / Grok — AI生成内容仅供参考")
