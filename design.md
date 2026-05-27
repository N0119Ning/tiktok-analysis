<!-- Design System -->

<!DOCTYPE html><html class="light" lang="zh-CN" style=""><head>

<meta charset="utf-8">

<meta content="width=device-width, initial-scale=1.0" name="viewport">

<title>AI 评论分析助手 - 追问交互</title>

<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700\&amp;family=JetBrains+Mono:wght@400;500\&amp;display=swap" rel="stylesheet">

<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1\&amp;display=swap" rel="stylesheet">

<style>

&#x20;       .material-symbols-outlined {

&#x20;           font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;

&#x20;       }

&#x20;       .chat-container::-webkit-scrollbar {

&#x20;           width: 6px;

&#x20;       }

&#x20;       .chat-container::-webkit-scrollbar-track {

&#x20;           background: transparent;

&#x20;       }

&#x20;       .chat-container::-webkit-scrollbar-thumb {

&#x20;           background: #e5e7eb;

&#x20;           border-radius: 10px;

&#x20;       }

&#x20;       @keyframes subtle-pulse {

&#x20;           0%, 100% { opacity: 1; }

&#x20;           50% { opacity: 0.6; }

&#x20;       }

&#x20;       .reasoning-pulse {

&#x20;           animation: subtle-pulse 2s infinite ease-in-out;

&#x20;       }

&#x20;   </style>

<script id="tailwind-config">tailwind.config = {darkMode: "class", theme: {extend: {colors: {"secondary-fixed-dim": "#b4c6f4", error: "#ba1a1a", "inverse-surface": "#2f3036", background: "#faf9ff", "on-primary": "#ffffff", "on-primary-container": "#fefcff", "on-secondary-fixed-variant": "#34466d", "outline-variant": "#c3c6d3", "surface-bright": "#faf9ff", "on-surface": "#1a1b20", "surface-variant": "#e2e2e9", "tertiary-fixed-dim": "#d0c6ac", "surface-container-high": "#e8e7ee", "inverse-primary": "#acc7ff", "on-secondary-fixed": "#041a3f", tertiary: "#635c46", "surface-container-highest": "#e2e2e9", "surface-tint": "#3d5e99", "primary-fixed": "#d7e2ff", "on-surface-variant": "#434751", "surface-container-lowest": "#ffffff", "inverse-on-surface": "#f1f0f7", "primary-container": "#5474b1", surface: "#faf9ff", "on-tertiary-fixed": "#201b0b", "on-tertiary": "#ffffff", "on-tertiary-container": "#fffbff", "on-secondary": "#ffffff", "on-error-container": "#93000a", "surface-dim": "#dad9e0", "on-background": "#1a1b20", "primary-fixed-dim": "#acc7ff", "on-error": "#ffffff", "on-secondary-container": "#475981", "surface-container": "#eeedf4", "error-container": "#ffdad6", primary: "#3a5b97", "on-primary-fixed": "#001a40", secondary: "#4c5e86", "surface-container-low": "#f3f3fa", "on-primary-fixed-variant": "#224680", "tertiary-container": "#7c745e", "secondary-fixed": "#d8e2ff", "tertiary-fixed": "#ede2c7", "on-tertiary-fixed-variant": "#4d4633", outline: "#737783", "secondary-container": "#bfd1ff"}, borderRadius: {DEFAULT: "1rem", lg: "2rem", xl: "3rem", full: "9999px"}, spacing: {sm: "12px", xl: "32px", xs: "8px", "container-max": "1440px", lg: "24px", gutter: "24px", "3xl": "64px", "margin-mobile": "16px", base: "4px", md: "16px", "2xl": "48px"}, fontFamily: {"headline-md": \["Inter"], "label-sm": \["Inter"], "body-lg": \["Inter"], "headline-lg": \["Inter"], "body-md": \["Inter"], "headline-lg-mobile": \["Inter"], "mono-data": \["JetBrains Mono"], "label-md": \["Inter"], "display-lg": \["Inter"], headline: \["Inter"], display: \["Inter"], body: \["Inter"], label: \["Inter"]}, fontSize: {"headline-md": \["24px", {lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600"}], "label-sm": \["12px", {lineHeight: "16px", letterSpacing: "0.02em", fontWeight: "600"}], "body-lg": \["18px", {lineHeight: "28px", letterSpacing: "0", fontWeight: "400"}], "headline-lg": \["32px", {lineHeight: "40px", letterSpacing: "-0.02em", fontWeight: "600"}], "body-md": \["16px", {lineHeight: "24px", letterSpacing: "0", fontWeight: "400"}], "headline-lg-mobile": \["24px", {lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600"}], "mono-data": \["13px", {lineHeight: "20px", letterSpacing: "0", fontWeight: "400"}], "label-md": \["14px", {lineHeight: "20px", letterSpacing: "0.01em", fontWeight: "500"}], "display-lg": \["48px", {lineHeight: "56px", letterSpacing: "-0.02em", fontWeight: "700"}]}}}};</script>

</head>

<body class="bg-background text-on-surface font-body-md antialiased overflow-hidden">

<div class="flex h-screen w-full">

<!-- SideNavBar - JSON Specified Layout -->

<aside class="hidden md:flex flex-col h-full p-md gap-base bg-surface-container-low dark:bg-inverse-surface border-r border-outline-variant w-64 flex-shrink-0 z-30">

<div class="flex items-center gap-sm mb-xl px-sm">

<div class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center text-on-primary">

<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">analytics</span>

</div>

<div>

<h1 class="font-headline-md text-label-md font-bold text-primary">当前项目</h1>

<p class="text-on-surface-variant font-label-sm">第四季度评论分析</p>

</div>

</div>

<nav class="flex flex-col gap-xs">

<div class="flex items-center gap-md text-on-surface-variant dark:text-surface-variant px-md py-sm hover:bg-surface-container-high dark:hover:bg-surface-variant rounded-lg transition-all cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined" data-icon="cloud\_upload">cloud\_upload</span>

<span class="font-label-md text-label-md">上传与规划</span>

</div>

<div class="flex items-center gap-md text-on-surface-variant dark:text-surface-variant px-md py-sm hover:bg-surface-container-high dark:hover:bg-surface-variant rounded-lg transition-all cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined" data-icon="analytics">analytics</span>

<span class="font-label-md text-label-md">分析报告</span>

</div>

<div class="flex items-center gap-md bg-secondary-container dark:bg-secondary text-on-secondary-container dark:text-on-secondary rounded-lg px-md py-sm cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined" data-icon="chat\_bubble" style="font-variation-settings: 'FILL' 1;">chat\_bubble</span>

<span class="font-label-md text-label-md">追问交互</span>

</div>

</nav>

<div class="mt-auto pt-lg border-t border-outline-variant">

<div class="flex items-center gap-sm p-sm rounded-xl hover:bg-surface-container-high transition-colors cursor-pointer">

<img alt="User" class="w-8 h-8 rounded-full border border-outline-variant" data-alt="A professional high-resolution headshot of a software engineer in their late 20s, with a friendly expression. The background is a blurred office environment with soft blue and white highlights, maintaining a clean and minimalist light-mode aesthetic consistent with a premium SaaS application profile picture." src="https://lh3.googleusercontent.com/aida-public/AB6AXuB7zRRcbASq4\_ivdk4j7oUTCHAMYiNnic5tDxsPhXdkltt94kHaHZGCDYtXBvx9hGS1WQv4KgTwAqJRcSL\_wjDD3VmpEpIVSdE6RzR4QVOVa9dJwZUTh0RUDXNaEbzhxuGxE3fVYxTpNsF7LeIWll9sBvu1\_JPJqA3D\_q\_xCtCAi9sZK2TWLOkjOrWEtSWmWYYFayVckiL23IkJ3P43CHTD1q6bZoLtobZ0FsUy-1RcT2lKqGkYuVEC0FCiITIxkKT6Xx6DEPQsutl\_">

<div class="flex-1 overflow-hidden">

<p class="font-label-md text-label-md truncate">Alex Chen</p>

<p class="text-on-surface-variant font-label-sm truncate">Product Lead</p>

</div>

<span class="material-symbols-outlined text-on-surface-variant">more\_vert</span>

</div>

</div>

</aside>

<!-- Main Content Area -->

<main class="flex-1 flex flex-col h-full bg-background relative">

<!-- TopNavBar - JSON Specified Layout -->

<header class="flex justify-between items-center px-lg py-sm w-full sticky top-0 z-50 bg-surface dark:bg-inverse-surface border-b border-outline-variant dark:border-outline shadow-sm h-16">

<div class="flex items-center gap-md">

<span class="md:hidden material-symbols-outlined cursor-pointer">menu</span>

<span class="font-headline-md text-headline-md font-bold text-primary dark:text-primary-fixed-dim">AI 评论分析助手</span>

</div>

<div class="flex items-center gap-md">

<button class="flex items-center gap-xs px-md py-sm text-primary font-label-md hover:bg-primary-container/10 rounded-lg transition-colors" onclick="location.reload()">

<span class="material-symbols-outlined text-sm">delete\_sweep</span>

&#x20;                       清除聊天记录

&#x20;                   </button>

<div class="h-6 w-px bg-outline-variant mx-sm"></div>

<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors" data-icon="notifications">notifications</span>

<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors" data-icon="settings">settings</span>

</div>

</header>

<!-- Chat Canvas -->

<div class="flex-1 overflow-y-auto chat-container flex flex-col items-center py-2xl">

<div class="w-full max-w-4xl px-lg flex flex-col gap-xl">

<!-- Message: User -->

<div class="flex flex-col items-end animate-in fade-in slide-in-from-bottom-4 duration-500">

<div class="max-w-\[80%] bg-surface-container-high rounded-2xl px-lg py-md text-on-surface shadow-sm border border-outline-variant/30">

<p class="font-body-md text-body-md">1星评价最常见的原因是什么？</p>

</div>

<span class="text-on-surface-variant font-label-sm mt-xs mr-sm">刚刚</span>

</div>

<!-- Message: AI -->

<div class="flex flex-col items-start animate-in fade-in slide-in-from-bottom-6 duration-700">

<div class="flex gap-md w-full">

<div class="w-10 h-10 rounded-full bg-primary flex-shrink-0 flex items-center justify-center text-on-primary shadow-lg">

<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">smart\_toy</span>

</div>

<div class="flex-1 flex flex-col gap-sm">

<div class="bg-surface rounded-2xl rounded-tl-none px-lg py-md text-on-surface border border-outline-variant shadow-sm ring-1 ring-black/5">

<p class="font-body-md text-body-md leading-relaxed">

&#x20;                                       根据分析，<span class="font-bold text-primary">65%的1星评价</span>与<span class="bg-error/10 text-error px-1 rounded">v2.1版本更新后的“账号登录”失败</span>有关。

&#x20;                                   </p>

</div>

<!-- Reasoning Block (Expandable) -->

<details class="group border border-outline-variant rounded-xl overflow-hidden bg-surface-container-lowest">

<summary class="flex items-center justify-between px-md py-sm cursor-pointer hover:bg-surface-container-low transition-colors list-none">

<div class="flex items-center gap-sm">

<span class="material-symbols-outlined text-primary text-sm">cognition</span>

<span class="font-label-sm text-on-surface-variant">思考链</span>

</div>

<span class="material-symbols-outlined text-on-surface-variant group-open:rotate-180 transition-transform duration-300">expand\_more</span>

</summary>

<div class="px-md py-md border-t border-outline-variant bg-surface-container-lowest/50">

<div class="font-mono-data text-mono-data text-on-surface-variant space-y-2">

<div class="flex gap-sm">

<span class="text-outline">1.</span>

<span class="">过滤条件：<code class="text-primary">评分 == 1</code> (N=1,420 条评论)</span>

</div>

<div class="flex gap-sm">

<span class="text-outline">2.</span>

<span class="">分类：NLP 聚类识别出的主要主题。</span>

</div>

<div class="flex gap-sm">

<span class="text-outline">3.</span>

<span class="">关键词提取：匹配 <span class="italic">'登录', '验证', '失败', '错误'</span>。</span>

</div>

<div class="flex gap-sm">

<span class="text-outline">4.</span>

<span class="">时间关联：峰值与 <code class="bg-surface-variant px-1 rounded">Release v2.1 (11月12日)</code> 一致。</span>

</div>

</div>

</div>

</details>

<div class="flex gap-sm">

<button class="p-xs hover:bg-surface-container-high rounded-full transition-colors text-on-surface-variant">

<span class="material-symbols-outlined text-sm">thumb\_up</span>

</button>

<button class="p-xs hover:bg-surface-container-high rounded-full transition-colors text-on-surface-variant">

<span class="material-symbols-outlined text-sm">thumb\_down</span>

</button>

<button class="p-xs hover:bg-surface-container-high rounded-full transition-colors text-on-surface-variant">

<span class="material-symbols-outlined text-sm">content\_copy</span>

</button>

</div>

</div>

</div>

</div>

<!-- AI Reasoning Placeholder (Active) -->

<div class="flex items-start gap-md opacity-0 transition-opacity duration-300" id="ai-typing">

<div class="w-10 h-10 rounded-full bg-primary flex-shrink-0 flex items-center justify-center text-on-primary reasoning-pulse">

<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">smart\_toy</span>

</div>

<div class="bg-surface rounded-2xl rounded-tl-none px-lg py-sm text-on-surface-variant border border-outline-variant shadow-sm flex items-center gap-md">

<div class="flex gap-1">

<div class="w-2 h-2 rounded-full bg-primary animate-bounce"></div>

<div class="w-2 h-2 rounded-full bg-primary animate-bounce \[animation-delay:-.3s]"></div>

<div class="w-2 h-2 rounded-full bg-primary animate-bounce \[animation-delay:-.5s]"></div>

</div>

<span class="font-label-md text-label-md italic">AI 正在思考...</span>

</div>

</div>

</div>

</div>

<!-- Input Area -->

<div class="p-lg border-t border-outline-variant bg-surface sticky bottom-0 z-40">

<div class="max-w-4xl mx-auto flex flex-col gap-md">

<!-- Info Banner -->

<div class="bg-primary-container/10 border border-primary/20 rounded-xl px-md py-sm flex items-center gap-sm">

<span class="material-symbols-outlined text-primary text-sm">info</span>

<p class="font-label-sm text-primary">上下文：<span class="font-bold">Review Analysis v2.1 已激活</span>。详细数据可供查询。</p>

</div>

<div class="relative group">

<textarea class="w-full bg-surface-container-low border border-outline-variant rounded-2xl px-lg py-md pr-32 focus:ring-2 focus:ring-primary focus:border-primary transition-all resize-none font-body-md text-body-md placeholder:text-on-surface-variant/50" id="chat-input" placeholder="问我：最严重的问题是什么？/ 建议如何修复登录漏洞..." rows="1"></textarea>

<div class="absolute right-3 bottom-3 flex items-center gap-sm">

<button class="p-xs text-on-surface-variant hover:text-primary transition-colors">

<span class="material-symbols-outlined">attach\_file</span>

</button>

<button class="bg-primary text-on-primary px-lg py-sm rounded-xl font-label-md flex items-center gap-sm hover:bg-primary-container shadow-md active:scale-95 transition-all" id="send-btn">

<span class="">发送</span>

<span class="material-symbols-outlined text-sm">send</span>

</button>

</div>

</div>



</div>

</div>

</main>

<!-- Contextual Panel (Hidden on smaller screens) -->

<aside class="hidden lg:flex flex-col w-80 bg-surface border-l border-outline-variant p-lg gap-lg overflow-y-auto">

<h3 class="font-headline-md text-label-md font-bold text-on-surface">数据快照</h3>

<div class="flex flex-col gap-md">

<div class="p-md rounded-xl bg-surface-container border border-outline-variant">

<p class="font-label-sm text-on-surface-variant mb-xs">净情绪得分</p>

<div class="flex items-center gap-md">

<span class="text-headline-md font-bold text-error">32.4</span>

<div class="flex-1 h-2 bg-outline-variant rounded-full overflow-hidden">

<div class="h-full bg-error" style="width: 32%"></div>

</div>

</div>

<p class="font-label-sm text-error mt-xs">▼ 12% 较上次更新</p>

</div>

<div class="space-y-sm">

<p class="font-label-sm font-bold text-on-surface-variant uppercase tracking-wider">高频实体</p>

<div class="flex flex-wrap gap-xs">

<span class="px-sm py-xs bg-surface-container-high rounded-full font-label-sm border border-outline-variant">#登录流程</span>

<span class="px-sm py-xs bg-surface-container-high rounded-full font-label-sm border border-outline-variant">#验证服务器</span>

<span class="px-sm py-xs bg-surface-container-high rounded-full font-label-sm border border-outline-variant">#UI延迟</span>

<span class="px-sm py-xs bg-surface-container-high rounded-full font-label-sm border border-outline-variant">#v2.1更新</span>

</div>

</div>

<div class="mt-lg">

</div>

</div>

</aside>

</div>

<!-- Footer - JSON Specified Layout -->

<footer class="flex justify-between items-center px-lg py-sm w-full mt-auto bg-surface dark:bg-inverse-surface border-t border-outline-variant dark:border-outline fixed bottom-0 left-0 md:left-64 md:w-\[calc(100%-16rem)] z-20">

<div class="flex items-center gap-md">

<span class="font-label-md text-label-md font-bold text-on-surface-variant dark:text-surface-variant">© 2024 AI 评论分析助手.</span>

<span class="font-label-sm text-primary">系统状态：运行良好。</span>

</div>

<div class="flex gap-lg">







</div>

</footer>

<script>

&#x20;       const input = document.getElementById('chat-input');

&#x20;       const sendBtn = document.getElementById('send-btn');

&#x20;       const aiTyping = document.getElementById('ai-typing');



&#x20;       // Auto-resize textarea

&#x20;       input.addEventListener('input', () => {

&#x20;           input.style.height = 'auto';

&#x20;           input.style.height = (input.scrollHeight) + 'px';

&#x20;       });



&#x20;       // Simulate AI Thinking

&#x20;       sendBtn.addEventListener('click', () => {

&#x20;           if(input.value.trim() === "") return;

&#x20;           

&#x20;           const message = input.value;

&#x20;           input.value = "";

&#x20;           input.style.height = 'auto';

&#x20;           

&#x20;           // Show typing indicator

&#x20;           aiTyping.style.opacity = "1";

&#x20;           sendBtn.disabled = true;

&#x20;           sendBtn.innerHTML = `

&#x20;               <div class="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin"></div>

&#x20;               <span>思考中...</span>

&#x20;           `;



&#x20;           setTimeout(() => {

&#x20;               aiTyping.style.opacity = "0";

&#x20;               sendBtn.disabled = false;

&#x20;               sendBtn.innerHTML = `

&#x20;                   <span>发送</span>

&#x20;                   <span class="material-symbols-outlined text-sm">send</span>

&#x20;               `;

&#x20;               alert("这是演示界面。AI 逻辑将会处理: " + message);

&#x20;           }, 3000);

&#x20;       });



&#x20;       // Enter to send

&#x20;       input.addEventListener('keypress', (e) => {

&#x20;           if (e.key === 'Enter' \&\& !e.shiftKey) {

&#x20;               e.preventDefault();

&#x20;               sendBtn.click();

&#x20;           }

&#x20;       });

&#x20;   </script>

</body></html>



<!-- 追问交互 - AI 评论分析 Agent (中文版) -->

<!DOCTYPE html><html class="light" lang="zh-CN" style=""><head>

<meta charset="utf-8">

<meta content="width=device-width, initial-scale=1.0" name="viewport">

<title>AI 评论分析助手 - 上传与规划</title>

<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700\&amp;family=JetBrains+Mono\&amp;display=swap" rel="stylesheet">

<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1\&amp;display=swap" rel="stylesheet">

<script id="tailwind-config">

&#x20;       tailwind.config = {

&#x20;           darkMode: "class",

&#x20;           theme: {

&#x20;               extend: {

&#x20;                   colors: {

&#x20;                       "surface-tint": "#3d5e99",

&#x20;                       "surface-container-low": "#f3f3fa",

&#x20;                       "on-tertiary-fixed": "#201b0b",

&#x20;                       "on-secondary-fixed": "#041a3f",

&#x20;                       "on-primary-fixed": "#001a40",

&#x20;                       "error-container": "#ffdad6",

&#x20;                       "secondary-fixed-dim": "#b4c6f4",

&#x20;                       "on-error-container": "#93000a",

&#x20;                       "tertiary": "#655e49",

&#x20;                       "inverse-surface": "#2f3036",

&#x20;                       "surface-bright": "#faf9ff",

&#x20;                       "surface-container-lowest": "#ffffff",

&#x20;                       "on-tertiary": "#ffffff",

&#x20;                       "background": "#faf9ff",

&#x20;                       "on-surface-variant": "#434750",

&#x20;                       "on-secondary": "#ffffff",

&#x20;                       "surface-container": "#eeedf4",

&#x20;                       "on-secondary-container": "#475981",

&#x20;                       "primary-container": "#7e9ede",

&#x20;                       "tertiary-container": "#a69d85",

&#x20;                       "surface-variant": "#e2e2e9",

&#x20;                       "on-error": "#ffffff",

&#x20;                       "secondary-fixed": "#d8e2ff",

&#x20;                       "on-primary": "#ffffff",

&#x20;                       "tertiary-fixed-dim": "#d0c6ac",

&#x20;                       "outline-variant": "#c4c6d1",

&#x20;                       "on-primary-fixed-variant": "#224680",

&#x20;                       "on-background": "#1a1b20",

&#x20;                       "outline": "#747781",

&#x20;                       "on-surface": "#1a1b20",

&#x20;                       "inverse-primary": "#acc7ff",

&#x20;                       "surface": "#faf9ff",

&#x20;                       "surface-dim": "#dad9e0",

&#x20;                       "secondary": "#4c5e86",

&#x20;                       "primary-fixed-dim": "#acc7ff",

&#x20;                       "on-tertiary-container": "#3b3522",

&#x20;                       "tertiary-fixed": "#ede2c7",

&#x20;                       "on-secondary-fixed-variant": "#34466d",

&#x20;                       "primary": "#3d5e99",

&#x20;                       "on-primary-container": "#08346d",

&#x20;                       "surface-container-highest": "#e2e2e9",

&#x20;                       "inverse-on-surface": "#f1f0f7",

&#x20;                       "error": "#ba1a1a",

&#x20;                       "secondary-container": "#bfd1ff",

&#x20;                       "primary-fixed": "#d7e2ff",

&#x20;                       "on-tertiary-fixed-variant": "#4d4633",

&#x20;                       "surface-container-high": "#e8e7ee"

&#x20;                   },

&#x20;                   borderRadius: {

&#x20;                       "DEFAULT": "1rem",

&#x20;                       "lg": "2rem",

&#x20;                       "xl": "3rem",

&#x20;                       "full": "9999px"

&#x20;                   },

&#x20;                   spacing: {

&#x20;                       "xs": "8px",

&#x20;                       "sm": "12px",

&#x20;                       "xl": "32px",

&#x20;                       "margin-mobile": "16px",

&#x20;                       "md": "16px",

&#x20;                       "base": "4px",

&#x20;                       "gutter": "24px",

&#x20;                       "container-max": "1440px",

&#x20;                       "3xl": "64px",

&#x20;                       "lg": "24px",

&#x20;                       "2xl": "48px"

&#x20;                   },

&#x20;                   fontFamily: {

&#x20;                       "label-sm": \["Inter"],

&#x20;                       "headline-md": \["Inter"],

&#x20;                       "headline-lg-mobile": \["Inter"],

&#x20;                       "body-md": \["Inter"],

&#x20;                       "label-md": \["Inter"],

&#x20;                       "mono-data": \["JetBrains Mono"],

&#x20;                       "display-lg": \["Inter"],

&#x20;                       "headline-lg": \["Inter"],

&#x20;                       "body-lg": \["Inter"]

&#x20;                   },

&#x20;                   fontSize: {

&#x20;                       "label-sm": \["12px", { "lineHeight": "16px", "letterSpacing": "0.02em", "fontWeight": "600" }],

&#x20;                       "headline-md": \["24px", { "lineHeight": "32px", "letterSpacing": "-0.01em", "fontWeight": "600" }],

&#x20;                       "headline-lg-mobile": \["24px", { "lineHeight": "32px", "letterSpacing": "-0.01em", "fontWeight": "600" }],

&#x20;                       "body-md": \["16px", { "lineHeight": "24px", "letterSpacing": "0", "fontWeight": "400" }],

&#x20;                       "label-md": \["14px", { "lineHeight": "20px", "letterSpacing": "0.01em", "fontWeight": "500" }],

&#x20;                       "mono-data": \["13px", { "lineHeight": "20px", "letterSpacing": "0", "fontWeight": "400" }],

&#x20;                       "display-lg": \["48px", { "lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "700" }],

&#x20;                       "headline-lg": \["32px", { "lineHeight": "40px", "letterSpacing": "-0.02em", "fontWeight": "600" }],

&#x20;                       "body-lg": \["18px", { "lineHeight": "28px", "letterSpacing": "0", "fontWeight": "400" }]

&#x20;                   }

&#x20;               },

&#x20;           },

&#x20;       };

&#x20;   </script>

<style>

&#x20;       body {

&#x20;           background-color: #f8f9fa;

&#x20;           color: #191c1d;

&#x20;           font-family: 'Inter', sans-serif;

&#x20;       }

&#x20;       .material-symbols-outlined {

&#x20;           font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;

&#x20;           vertical-align: middle;

&#x20;       }

&#x20;       .bento-grid {

&#x20;           display: grid;

&#x20;           grid-template-columns: repeat(12, 1fr);

&#x20;           gap: 24px;

&#x20;       }

&#x20;       .glass-card {

&#x20;           background: rgba(255, 255, 255, 0.8);

&#x20;           backdrop-filter: blur(8px);

&#x20;           border: 1px solid #e5e7eb;

&#x20;           box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);

&#x20;       }

&#x20;       .step-line::after {

&#x20;           content: '';

&#x20;           position: absolute;

&#x20;           left: 11px;

&#x20;           top: 24px;

&#x20;           bottom: -12px;

&#x20;           width: 2px;

&#x20;           background: #e1e3e4;

&#x20;       }

&#x20;       .step-line:last-child::after {

&#x20;           display: none;

&#x20;       }

&#x20;   </style>

</head>

<body class="flex min-h-screen">

<!-- SideNavBar -->

<aside class="hidden md:flex flex-col h-screen w-64 bg-surface-container-low dark:bg-inverse-surface border-r border-outline-variant sticky top-0 z-50 p-md gap-base">

<div class="mb-xl px-md">

<h1 class="font-headline-md text-headline-md font-bold text-primary">分析助手</h1>

</div>

<div class="flex flex-col gap-base">

<div class="flex items-center gap-md bg-secondary-container text-on-secondary-container rounded-lg px-md py-sm cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined">cloud\_upload</span>

<span class="font-label-md text-label-md">上传与规划</span>

</div>

<div class="flex items-center gap-md text-on-surface-variant px-md py-sm hover:bg-surface-container-high rounded-lg transition-all cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined">analytics</span>

<span class="font-label-md text-label-md">分析报告</span>

</div>

<div class="flex items-center gap-md text-on-surface-variant px-md py-sm hover:bg-surface-container-high rounded-lg transition-all cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined">chat\_bubble</span>

<span class="font-label-md text-label-md">追问交互</span>

</div>

</div>

<div class="mt-auto pt-xl border-t border-outline-variant">

<div class="flex items-center gap-md px-md">



<div>





</div>

</div>

</div>

</aside>

<!-- Main Content Area -->

<main class="flex-1 flex flex-col min-w-0 bg-background">

<!-- TopNavBar -->

<header class="flex justify-between items-center px-lg py-sm w-full sticky top-0 z-40 bg-surface border-b border-outline-variant shadow-sm">

<div class="flex items-center gap-md">

<h2 class="font-headline-md text-headline-md font-bold text-primary">AI 评论分析助手</h2>

</div>

<div class="flex items-center gap-md">

<div class="flex gap-sm">

<span class="material-symbols-outlined text-on-surface-variant cursor-pointer active:opacity-80">notifications</span>

<span class="material-symbols-outlined text-on-surface-variant cursor-pointer active:opacity-80">settings</span>

</div>



</div>

</header>

<!-- Content Canvas -->

<div class="p-2xl max-w-\[1440px] mx-auto w-full">

<!-- Success Toast (Persistent) -->

<div class="mb-xl flex items-center justify-between bg-secondary-container/30 border border-secondary text-on-secondary-container px-lg py-sm rounded-xl animate-in fade-in slide-in-from-top-4 duration-500">

<div class="flex items-center gap-md">

<span class="material-symbols-outlined text-secondary">check\_circle</span>

<p class="font-body-md text-body-md font-medium">分析完成：已处理 1,150 条评论，置信度达 98%。</p>

</div>

<button class="material-symbols-outlined text-on-secondary-container hover:opacity-70">close</button>

</div>

<!-- Dashboard Content -->

<div class="bento-grid">

<!-- Left Column: Actions \& Planning -->

<div class="col-span-12 lg:col-span-4 flex flex-col gap-lg">

<!-- Main Action Card -->

<section class="glass-card rounded-xl p-lg flex flex-col gap-md" style="transform: translateY(0px); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);">

<h3 class="font-headline-md text-headline-md text-on-surface">数据编排</h3>

<div class="flex flex-col gap-sm mt-md">

<button class="w-full bg-primary text-on-primary font-label-md text-label-md py-md rounded-lg flex items-center justify-center gap-sm hover:brightness-110 active:scale-\[0.98] transition-all">

<span class="material-symbols-outlined">upload\_file</span>

&#x20;                           上传 CSV

&#x20;                       </button>

<button class="w-full bg-surface-container-high text-on-surface-variant font-label-md text-label-md py-md rounded-lg flex items-center justify-center gap-sm cursor-not-allowed opacity-60" disabled="">

<span class="material-symbols-outlined">auto\_fix\_high</span>

&#x20;                           生成方案

&#x20;                       </button>

<button class="w-full border-2 border-primary text-primary font-label-md text-label-md py-md rounded-lg flex items-center justify-center gap-sm hover:bg-primary/5 active:scale-\[0.98] transition-all">

<span class="material-symbols-outlined">play\_arrow</span>

&#x20;                           开始分析

&#x20;                       </button>

</div>

</section>

<!-- Analysis Plan Card -->

<section class="glass-card rounded-xl p-lg" style="transform: translateY(0px); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);">

<div class="flex justify-between items-center mb-lg">

<h3 class="font-label-md text-label-md font-bold text-on-surface-variant uppercase tracking-wider">分析策略</h3>

<span class="px-sm py-1 bg-tertiary/10 text-tertiary text-\[10px] font-bold rounded-full border border-tertiary/20">自定义流程</span>

</div>

<div class="flex flex-col gap-md relative">

<div class="step-line relative flex gap-md items-start">

<div class="w-6 h-6 rounded-full bg-primary text-on-primary flex items-center justify-center z-10 shrink-0">

<span class="text-\[12px] font-bold">1</span>

</div>

<div>

<p class="font-label-md text-label-md font-bold">情感量化</p>

<p class="text-\[12px] text-on-surface-variant">Llama-3-70B 深度评分</p>

</div>

</div>

<div class="step-line relative flex gap-md items-start">

<div class="w-6 h-6 rounded-full bg-primary text-on-primary flex items-center justify-center z-10 shrink-0">

<span class="text-\[12px] font-bold">2</span>

</div>

<div>

<p class="font-label-md text-label-md font-bold">主题聚类</p>

<p class="text-\[12px] text-on-surface-variant">向量数据库语义搜索</p>

</div>

</div>

<div class="step-line relative flex gap-md items-start">

<div class="w-6 h-6 rounded-full bg-surface-container-highest text-on-surface-variant flex items-center justify-center z-10 shrink-0 border border-outline-variant">

<span class="text-\[12px] font-bold">3</span>

</div>

<div>

<p class="font-label-md text-label-md font-bold">根本原因分析</p>

<p class="text-\[12px] text-on-surface-variant">竞争对手上下文对比</p>

</div>

</div>

</div>

<!-- Risk Hint -->

<div class="mt-xl p-md bg-error-container/20 border-l-4 border-error rounded-r-lg">

<div class="flex items-center gap-sm mb-1 text-error">

<span class="material-symbols-outlined text-\[18px]">warning</span>

<span class="text-\[11px] font-bold uppercase">风险提示</span>

</div>

<p class="text-on-surface-variant text-label-sm font-body-md">注意：检测到大量短评。已调整过滤阈值以减少噪音。</p>

</div>

</section>

</div>

<!-- Right Column: Status \& Overview -->

<div class="col-span-12 lg:col-span-8 flex flex-col gap-lg">

<!-- Data Overview Bento Item -->

<div class="grid grid-cols-1 md:grid-cols-2 gap-lg">

<section class="glass-card rounded-xl p-lg relative overflow-hidden group" style="transform: translateY(0px); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);">

<div class="absolute -right-8 -top-8 w-32 h-32 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all duration-700"></div>

<div class="flex items-center gap-md mb-lg">

<div class="p-sm bg-primary/10 rounded-lg text-primary">

<span class="material-symbols-outlined">description</span>

</div>

<div>

<h4 class="font-label-md text-label-md font-bold text-on-surface">reviews\_2024\_q4.csv</h4>

<p class="text-label-sm text-on-surface-variant">源文件</p>

</div>

</div>

<div class="grid grid-cols-2 gap-md">

<div class="p-sm bg-surface-container-low rounded-lg">

<p class="text-\[10px] text-on-surface-variant uppercase font-bold">总评论数</p>

<p class="font-headline-md text-headline-md text-primary">1,240</p>

</div>

<div class="p-sm bg-surface-container-low rounded-lg">

<p class="text-\[10px] text-on-surface-variant uppercase font-bold">语言</p>

<p class="font-headline-md text-headline-md text-on-surface">ZH-CN</p>

</div>

</div>

</section>

<section class="glass-card rounded-xl p-lg" style="transform: translateY(0px); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);">

<h4 class="font-label-md text-label-md font-bold mb-md text-on-surface-variant">列映射</h4>

<div class="space-y-sm">

<div class="flex justify-between items-center p-sm bg-surface-container-low rounded-lg border border-transparent hover:border-outline-variant transition-all">

<span class="text-label-sm font-medium">文本内容</span>

<span class="font-mono-data text-mono-data bg-white px-md py-1 rounded shadow-sm">"Content"</span>

</div>

<div class="flex justify-between items-center p-sm bg-surface-container-low rounded-lg border border-transparent hover:border-outline-variant transition-all">

<span class="text-label-sm font-medium">评分列</span>

<span class="font-mono-data text-mono-data bg-white px-md py-1 rounded shadow-sm">"Score"</span>

</div>

</div>

</section>

</div>

<!-- Pipeline Execution Status -->

<section class="glass-card rounded-xl p-xl" style="transform: translateY(0px); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);">

<div class="flex justify-between items-center mb-xl">

<h3 class="font-headline-md text-headline-md text-on-surface">流水线状态</h3>

<div class="flex items-center gap-sm">

<span class="relative flex h-3 w-3">

<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75"></span>

<span class="relative inline-flex rounded-full h-3 w-3 bg-secondary"></span>

</span>

<span class="text-label-sm font-bold text-secondary">正在运行</span>

</div>

</div>

<!-- Pipeline Steps -->

<div class="space-y-2xl">

<!-- Step 1 -->

<div class="space-y-md">

<div class="flex justify-between items-end">

<div>

<p class="text-label-sm font-bold text-primary-container bg-primary/10 px-sm py-1 rounded-full w-fit mb-2">步骤 1/3</p>

<h4 class="font-body-lg text-body-lg font-bold">数据清洗与向量化</h4>

</div>

<span class="font-mono-data text-mono-data text-secondary font-bold">100%</span>

</div>

<div class="w-full bg-surface-container-highest h-1 rounded-full overflow-hidden">

<div class="bg-secondary h-full w-full"></div>

</div>

<div class="bg-surface-container-low p-md rounded-lg flex items-center justify-between">

<div class="flex items-center gap-md">

<span class="material-symbols-outlined text-on-surface-variant" style="font-variation-settings: 'FILL' 1;">verified</span>

<p class="text-label-sm text-on-surface-variant italic">检查点 1: 已过滤 1,240 → 1,150</p>

</div>

<span class="text-\[11px] font-bold text-error">7.2% 已过滤 (字数 \&lt; 5)</span>

</div>

</div>

<!-- Step 2 -->

<div class="space-y-md">

<div class="flex justify-between items-end">

<div>

<p class="text-label-sm font-bold text-primary bg-primary/10 px-sm py-1 rounded-full w-fit mb-2">步骤 2/3</p>

<h4 class="font-body-lg text-body-lg font-bold">问题分类与深度 LLM 分析</h4>

</div>

<span class="font-mono-data text-mono-data text-primary font-bold">45%</span>

</div>

<div class="w-full bg-surface-container-highest h-1 rounded-full overflow-hidden">

<div class="bg-primary h-full w-\[45%] animate-pulse"></div>

</div>

<div class="flex gap-md mt-sm">

<div class="flex-1 p-sm border border-outline-variant border-dashed rounded-lg flex items-center justify-center gap-sm opacity-50">

<span class="material-symbols-outlined text-on-surface-variant">pending</span>

<span class="text-label-sm">高置信度 (待定)</span>

</div>

<div class="flex-1 p-sm border border-outline-variant border-dashed rounded-lg flex items-center justify-center gap-sm opacity-50">

<span class="material-symbols-outlined text-on-surface-variant">pending</span>

<span class="text-label-sm">质量指标 (待定)</span>

</div>

</div>

</div>

</div>

</section>

</div>

</div>

<!-- Welcome Empty State -->

<div class="fixed inset-0 z-50 flex items-center justify-center bg-surface/80 backdrop-blur-sm p-lg hidden" id="welcome-overlay" style="display: none;">

<div class="max-w-2xl w-full glass-card p-2xl rounded-2xl shadow-2xl relative" style="transform: translateY(0px); transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);">

<button class="absolute right-xl top-xl material-symbols-outlined hover:text-primary transition-colors" onclick="this.closest('#welcome-overlay').style.display='none'">close</button>

<div class="text-center mb-2xl">

<div class="w-20 h-20 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-lg">

<span class="material-symbols-outlined !text-\[48px]">auto\_awesome</span>

</div>

<h2 class="font-display-lg text-display-lg text-primary mb-sm">欢迎使用 AI 评论分析</h2>

<p class="font-body-lg text-body-lg text-on-surface-variant">您的智能层，将客户噪音转化为可落地的产品洞察。</p>

</div>

<div class="grid grid-cols-1 md:grid-cols-5 gap-md relative">

<!-- Connecting Line -->

<div class="hidden md:block absolute top-\[40px] left-\[10%] right-\[10%] h-\[2px] bg-outline-variant -z-10"></div>

<div class="flex flex-col items-center text-center gap-sm">

<div class="w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold">1</div>

<p class="text-label-sm font-bold">上传 CSV</p>

</div>

<div class="flex flex-col items-center text-center gap-sm">

<div class="w-10 h-10 rounded-full bg-surface-container-highest text-on-surface-variant border border-outline-variant flex items-center justify-center font-bold">2</div>

<p class="text-label-sm font-bold">自动检测</p>

</div>

<div class="flex flex-col items-center text-center gap-sm">

<div class="w-10 h-10 rounded-full bg-surface-container-highest text-on-surface-variant border border-outline-variant flex items-center justify-center font-bold">3</div>

<p class="text-label-sm font-bold">制定策略</p>

</div>

<div class="flex flex-col items-center text-center gap-sm">

<div class="w-10 h-10 rounded-full bg-surface-container-highest text-on-surface-variant border border-outline-variant flex items-center justify-center font-bold">4</div>

<p class="text-label-sm font-bold">AI 分析</p>

</div>

<div class="flex flex-col items-center text-center gap-sm">

<div class="w-10 h-10 rounded-full bg-surface-container-highest text-on-surface-variant border border-outline-variant flex items-center justify-center font-bold">5</div>

<p class="text-label-sm font-bold">质量检查</p>

</div>

</div>

<div class="mt-2xl flex justify-center">

<button class="px-3xl py-md bg-primary text-on-primary rounded-xl font-bold hover:brightness-110 active:scale-95 transition-all" onclick="this.closest('#welcome-overlay').style.display='none'">开始使用</button>

</div>

</div>

</div>

</div>

<!-- Footer -->

<footer class="flex justify-between items-center px-lg py-sm w-full mt-auto border-t border-outline-variant bg-surface">

<div class="flex gap-xl">

<span class="font-label-md text-label-md font-bold text-on-surface-variant">AI 评论分析助手</span>



</div>

<div class="flex gap-lg">







</div>

</footer>

</main>

<script>

&#x20;   document.addEventListener('DOMContentLoaded', () => {

&#x20;       // Show welcome state by default for the demo

&#x20;       document.getElementById('welcome-overlay').style.display = 'flex';

&#x20;       

&#x20;       // Hover effect for bento cards

&#x20;       document.querySelectorAll('.glass-card').forEach(card => {

&#x20;           card.addEventListener('mouseenter', () => {

&#x20;               card.classList.add('shadow-md');

&#x20;               card.style.transform = 'translateY(-2px)';

&#x20;               card.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

&#x20;           });

&#x20;           card.addEventListener('mouseleave', () => {

&#x20;               card.classList.remove('shadow-md');

&#x20;               card.style.transform = 'translateY(0)';

&#x20;           });

&#x20;       });

&#x20;   });

</script>









</body></html>



<!-- 上传与规划 - AI 评论分析 Agent (中文版) -->

<!DOCTYPE html><html class="light" lang="zh-CN" style=""><head>

<meta charset="utf-8">

<meta content="width=device-width, initial-scale=1.0" name="viewport">

<title>分析报告 | AI 评论分析助手</title>

<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800\&amp;family=JetBrains+Mono:wght@400;500\&amp;display=swap" rel="stylesheet">

<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1\&amp;display=swap" rel="stylesheet">

<script id="tailwind-config">

&#x20;       tailwind.config = {

&#x20;           darkMode: "class",

&#x20;           theme: {

&#x20;               extend: {

&#x20;                   colors: {

&#x20;                       "surface-tint": "#3d5e99",

&#x20;                       "surface-container-low": "#f3f3fa",

&#x20;                       "on-tertiary-fixed": "#201b0b",

&#x20;                       "on-secondary-fixed": "#041a3f",

&#x20;                       "on-primary-fixed": "#001a40",

&#x20;                       "error-container": "#ffdad6",

&#x20;                       "secondary-fixed-dim": "#b4c6f4",

&#x20;                       "on-error-container": "#93000a",

&#x20;                       "tertiary": "#655e49",

&#x20;                       "inverse-surface": "#2f3036",

&#x20;                       "surface-bright": "#faf9ff",

&#x20;                       "surface-container-lowest": "#ffffff",

&#x20;                       "on-tertiary": "#ffffff",

&#x20;                       "background": "#faf9ff",

&#x20;                       "on-surface-variant": "#434750",

&#x20;                       "on-secondary": "#ffffff",

&#x20;                       "surface-container": "#eeedf4",

&#x20;                       "on-secondary-container": "#475981",

&#x20;                       "primary-container": "#7e9ede",

&#x20;                       "tertiary-container": "#a69d85",

&#x20;                       "surface-variant": "#e2e2e9",

&#x20;                       "on-error": "#ffffff",

&#x20;                       "secondary-fixed": "#d8e2ff",

&#x20;                       "on-primary": "#ffffff",

&#x20;                       "tertiary-fixed-dim": "#d0c6ac",

&#x20;                       "outline-variant": "#c4c6d1",

&#x20;                       "on-primary-fixed-variant": "#224680",

&#x20;                       "on-background": "#1a1b20",

&#x20;                       "outline": "#747781",

&#x20;                       "on-surface": "#1a1b20",

&#x20;                       "inverse-primary": "#acc7ff",

&#x20;                       "surface": "#faf9ff",

&#x20;                       "surface-dim": "#dad9e0",

&#x20;                       "secondary": "#4c5e86",

&#x20;                       "primary-fixed-dim": "#acc7ff",

&#x20;                       "on-tertiary-container": "#3b3522",

&#x20;                       "tertiary-fixed": "#ede2c7",

&#x20;                       "on-secondary-fixed-variant": "#34466d",

&#x20;                       "primary": "#3d5e99",

&#x20;                       "on-primary-container": "#08346d",

&#x20;                       "surface-container-highest": "#e2e2e9",

&#x20;                       "inverse-on-surface": "#f1f0f7",

&#x20;                       "error": "#ba1a1a",

&#x20;                       "secondary-container": "#bfd1ff",

&#x20;                       "primary-fixed": "#d7e2ff",

&#x20;                       "on-tertiary-fixed-variant": "#4d4633",

&#x20;                       "surface-container-high": "#e8e7ee"

&#x20;                   },

&#x20;                   borderRadius: {

&#x20;                       "DEFAULT": "1rem",

&#x20;                       "lg": "2rem",

&#x20;                       "xl": "3rem",

&#x20;                       "full": "9999px"

&#x20;                   },

&#x20;                   spacing: {

&#x20;                       "xs": "8px",

&#x20;                       "sm": "12px",

&#x20;                       "xl": "32px",

&#x20;                       "margin-mobile": "16px",

&#x20;                       "md": "16px",

&#x20;                       "base": "4px",

&#x20;                       "gutter": "24px",

&#x20;                       "container-max": "1440px",

&#x20;                       "3xl": "64px",

&#x20;                       "lg": "24px",

&#x20;                       "2xl": "48px"

&#x20;                   },

&#x20;                   fontFamily: {

&#x20;                       "label-sm": \["Inter"],

&#x20;                       "headline-md": \["Inter"],

&#x20;                       "headline-lg-mobile": \["Inter"],

&#x20;                       "body-md": \["Inter"],

&#x20;                       "label-md": \["Inter"],

&#x20;                       "mono-data": \["JetBrains Mono"],

&#x20;                       "display-lg": \["Inter"],

&#x20;                       "headline-lg": \["Inter"],

&#x20;                       "body-lg": \["Inter"]

&#x20;                   },

&#x20;                   fontSize: {

&#x20;                       "label-sm": \["12px", {lineHeight: "16px", letterSpacing: "0.02em", fontWeight: "600"}],

&#x20;                       "headline-md": \["24px", {lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600"}],

&#x20;                       "headline-lg-mobile": \["24px", {lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600"}],

&#x20;                       "body-md": \["16px", {lineHeight: "24px", letterSpacing: "0", fontWeight: "400"}],

&#x20;                       "label-md": \["14px", {lineHeight: "20px", letterSpacing: "0.01em", fontWeight: "500"}],

&#x20;                       "mono-data": \["13px", {lineHeight: "20px", letterSpacing: "0", fontWeight: "400"}],

&#x20;                       "display-lg": \["48px", {lineHeight: "56px", letterSpacing: "-0.02em", fontWeight: "700"}],

&#x20;                       "headline-lg": \["32px", {lineHeight: "40px", letterSpacing: "-0.02em", fontWeight: "600"}],

&#x20;                       "body-lg": \["18px", {lineHeight: "28px", letterSpacing: "0", fontWeight: "400"}]

&#x20;                   }

&#x20;               }

&#x20;           }

&#x20;       };

&#x20;   </script>

<style>

&#x20;       .material-symbols-outlined {

&#x20;           font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;

&#x20;       }

&#x20;       .tonal-layer-1 {

&#x20;           background-color: #ffffff;

&#x20;           border: 1px solid #e5e7eb;

&#x20;           box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);

&#x20;           border-radius: 12px;

&#x20;       }

&#x20;       .sentiment-bar {

&#x20;           width: 4px;

&#x20;           height: 100%;

&#x20;           position: absolute;

&#x20;           left: 0;

&#x20;           top: 0;

&#x20;       }

&#x20;       .scroll-hide::-webkit-scrollbar {

&#x20;           display: none;

&#x20;       }

&#x20;       .scroll-hide {

&#x20;           -ms-overflow-style: none;

&#x20;           scrollbar-width: none;

&#x20;       }

&#x20;       .accordion-item.expanded .accordion-content {

&#x20;           display: block;

&#x20;       }

&#x20;       .accordion-content {

&#x20;           display: none;

&#x20;       }

&#x20;   </style>

</head>

<body class="bg-background text-on-surface font-body-md selection:bg-primary-container selection:text-on-primary-container">

<div class="flex min-h-screen">

<!-- SideNavBar -->

<aside class="hidden md:flex flex-col h-screen w-64 bg-surface-container-low border-r border-outline-variant sticky top-0 z-50 p-md gap-base">

<div class="flex flex-col gap-xs mb-xl">

<div class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center mb-sm">

<span class="material-symbols-outlined text-on-primary">analytics</span>

</div>

<h2 class="font-headline-md text-headline-md font-bold text-primary">当前项目</h2>

<p class="font-label-md text-label-md text-on-surface-variant">Q4 评论分析</p>

</div>

<nav class="flex flex-col gap-base">

<div class="flex items-center gap-md text-on-surface-variant px-md py-sm hover:bg-surface-container-high rounded-lg transition-all cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined" data-icon="cloud\_upload">cloud\_upload</span>

<span class="font-label-md text-label-md">上传与规划</span>

</div>

<div class="flex items-center gap-md bg-secondary-container text-on-secondary-container rounded-lg px-md py-sm cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined" data-icon="analytics">analytics</span>

<span class="font-label-md text-label-md">分析报告</span>

</div>

<div class="flex items-center gap-md text-on-surface-variant px-md py-sm hover:bg-surface-container-high rounded-lg transition-all cursor-pointer active:scale-95 duration-200">

<span class="material-symbols-outlined" data-icon="chat\_bubble">chat\_bubble</span>

<span class="font-label-md text-label-md">追问交互</span>

</div>

</nav>

<div class="mt-auto pt-xl border-t border-outline-variant">

<div class="flex items-center gap-sm px-md py-sm">

<img alt="User Profile" class="w-8 h-8 rounded-full bg-surface-variant" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDGut0S1Uxj6wY9xltm3f8BVh7Tr-9BA1YOwKYSJW9J1Eum1zO9aRGZCVi9llefyR1JU44hgh\_SkUAvh1\_vnweoChzoQ3G1Wk66t403UlmBQcn5aB7o4Pgc35yjltmj7ZBooOiTv7iphV1wEtWWI41tfN1KKX\_3FhWlCYD1cCg594DUzp9UuPtWmEpg7lkiNUn3xjIVKIkYCI-lLqC7XyIhYJaCGBGYay\_0uKMw\_aQc9sSXWPP2kvi2QW0Z17FWp0HK4QIe7tjjjlH-">

<div class="flex flex-col">

<span class="font-label-md text-label-md font-bold">管理员</span>

<span class="font-label-sm text-label-sm text-on-surface-variant">高级会员计划</span>

</div>

</div>

</div>

</aside>

<main class="flex-1 flex flex-col min-w-0">

<!-- TopNavBar -->

<header class="flex justify-between items-center px-lg py-sm w-full sticky top-0 z-50 bg-surface border-b border-outline-variant shadow-sm">

<div class="flex items-center gap-md">

<h1 class="font-headline-md text-headline-md font-bold text-primary">AI 评论分析助手</h1>

</div>

<div class="flex items-center gap-md">

<button class="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md flex items-center gap-xs hover:opacity-90 active:scale-95 transition-all">

<span class="material-symbols-outlined" data-icon="download">download</span>

&#x20;                       下载完整结果 (JSON)

&#x20;                   </button>

<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors" data-icon="notifications">notifications</span>

<span class="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors" data-icon="settings">settings</span>

</div>

</header>

<!-- Scrollable Content -->

<div class="flex-1 p-lg md:p-2xl space-y-2xl">

<!-- 1. Global Overview -->

<section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-gutter">

<div class="tonal-layer-1 p-lg space-y-xs">

<p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">总评论数</p>

<h3 class="font-display-lg text-display-lg text-primary">1,150</h3>

<div class="flex items-center gap-xs text-secondary font-label-sm text-label-sm">

<span class="material-symbols-outlined text-\[16px]" data-icon="trending\_up">trending\_up</span>

<span class="">+12% 较上月</span>

</div>

</div>

<div class="tonal-layer-1 p-lg space-y-xs">

<p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">类别数</p>

<h3 class="font-display-lg text-display-lg text-on-surface">8</h3>

<p class="font-label-sm text-label-sm text-on-surface-variant">已映射数据源</p>

</div>

<div class="tonal-layer-1 p-lg space-y-xs">

<p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">平均评分</p>

<div class="flex items-baseline gap-xs">

<h3 class="font-display-lg text-display-lg text-on-surface">3.8</h3>

<span class="font-label-md text-label-md text-on-surface-variant">/ 5.0</span>

</div>

<div class="flex text-\[#FFB800]">

<span class="material-symbols-outlined fill-current" data-icon="star" style="font-variation-settings: 'FILL' 1;">star</span>

<span class="material-symbols-outlined fill-current" data-icon="star" style="font-variation-settings: 'FILL' 1;">star</span>

<span class="material-symbols-outlined fill-current" data-icon="star" style="font-variation-settings: 'FILL' 1;">star</span>

<span class="material-symbols-outlined fill-current" data-icon="star\_half" style="font-variation-settings: 'FILL' 1;">star\_half</span>

<span class="material-symbols-outlined" data-icon="star">star</span>

</div>

</div>

<div class="tonal-layer-1 p-lg space-y-xs">

<p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">负面情绪</p>

<h3 class="font-display-lg text-display-lg text-error">24%</h3>

<div class="w-full bg-surface-variant h-1 rounded-full overflow-hidden">

<div class="bg-error h-full" style="width: 24%"></div>

</div>

</div>

<div class="tonal-layer-1 p-lg space-y-xs border-l-4 border-l-error">

<p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">最严重问题</p>

<h3 class="font-headline-md text-headline-md text-on-surface leading-tight">性能问题</h3>

<span class="inline-flex items-center px-xs py-\[2px] bg-error/10 text-error rounded-md font-label-sm text-label-sm">高优先级</span>

</div>

</section>

<!-- 2. Charts Area -->

<section class="grid grid-cols-1 lg:grid-cols-12 gap-gutter">

<!-- Sentiment Dist -->

<div class="tonal-layer-1 p-lg lg:col-span-4 flex flex-col">

<div class="flex justify-between items-center mb-xl">

<h4 class="font-headline-md text-\[18px]">情绪分布</h4>

<span class="material-symbols-outlined text-on-surface-variant text-\[20px]" data-icon="info">info</span>

</div>

<div class="flex-1 flex items-center justify-center relative min-h-\[240px]">

<div class="w-48 h-48 rounded-full border-\[16px] border-secondary relative flex items-center justify-center">

<div class="absolute inset-0 w-full h-full rounded-full border-\[16px] border-surface-variant border-t-error border-r-surface-container rotate-45"></div>

<div class="text-center">

<p class="font-display-lg text-\[32px] text-on-surface">62%</p>

<p class="font-label-sm text-label-sm text-on-surface-variant">正面</p>

</div>

</div>

</div>

<div class="mt-xl flex flex-wrap gap-md justify-center">

<div class="flex items-center gap-xs">

<span class="w-3 h-3 rounded-full bg-secondary"></span>

<span class="font-label-sm text-label-sm">正面 (62%)</span>

</div>

<div class="flex items-center gap-xs">

<span class="w-3 h-3 rounded-full bg-surface-variant"></span>

<span class="font-label-sm text-label-sm">中性 (14%)</span>

</div>

<div class="flex items-center gap-xs">

<span class="w-3 h-3 rounded-full bg-error"></span>

<span class="font-label-sm text-label-sm">负面 (24%)</span>

</div>

</div>

</div>

<!-- Category Dist -->

<div class="tonal-layer-1 p-lg lg:col-span-8">

<div class="flex justify-between items-center mb-xl">

<h4 class="font-headline-md text-\[18px]">各类别指标对比</h4>

<div class="flex gap-sm">

<button class="px-sm py-xs bg-surface-container-high rounded font-label-sm text-label-sm">评论量</button>

<button class="px-sm py-xs hover:bg-surface-container-low rounded font-label-sm text-label-sm transition-colors">平均分</button>

</div>

</div>

<div class="space-y-md">

<div class="space-y-xs">

<div class="flex justify-between font-label-md text-label-md">

<span class="">UI设计</span>

<span class="font-mono-data text-mono-data">320 条评论</span>

</div>

<div class="w-full bg-surface-container h-3 rounded-full overflow-hidden">

<div class="bg-primary h-full" style="width: 85%"></div>

</div>

</div>

<div class="space-y-xs">

<div class="flex justify-between font-label-md text-label-md">

<span class="">性能</span>

<span class="font-mono-data text-mono-data">280 条评论</span>

</div>

<div class="w-full bg-surface-container h-3 rounded-full overflow-hidden">

<div class="bg-primary h-full" style="width: 70%"></div>

</div>

</div>

<div class="space-y-xs">

<div class="flex justify-between font-label-md text-label-md">

<span class="">定价</span>

<span class="font-mono-data text-mono-data">150 条评论</span>

</div>

<div class="w-full bg-surface-container h-3 rounded-full overflow-hidden">

<div class="bg-primary h-full" style="width: 45%"></div>

</div>

</div>

<div class="space-y-xs">

<div class="flex justify-between font-label-md text-label-md">

<span class="">客服支持</span>

<span class="font-mono-data text-mono-data">120 条评论</span>

</div>

<div class="w-full bg-surface-container h-3 rounded-full overflow-hidden">

<div class="bg-primary h-full" style="width: 35%"></div>

</div>

</div>

</div>

</div>

</section>

<!-- 3. Drill-down Analysis List -->

<section class="space-y-md">

<div class="flex items-center justify-between">

<h3 class="font-headline-md text-headline-md">具体分析</h3>

<div class="flex items-center gap-sm">

<span class="font-label-sm text-label-sm text-on-surface-variant">筛选严重程度:</span>

<select class="bg-surface border border-outline rounded-lg px-sm py-xs font-label-md text-label-md focus:outline-none focus:ring-2 focus:ring-primary">

<option>所有程度</option>

<option>仅限高严重度</option>

<option>仅限中严重度</option>

</select>

</div>

</div>

<!-- Accordion Item 1 (Expanded) -->

<div class="tonal-layer-1 overflow-hidden transition-all duration-300 accordion-item expanded">

<div class="flex items-center p-lg cursor-pointer hover:bg-surface-container-low transition-colors group" onclick="this.parentElement.classList.toggle('expanded')">

<div class="sentiment-bar bg-error"></div>

<div class="grid grid-cols-12 gap-lg w-full items-center">

<div class="col-span-4 flex items-center gap-md">

<span class="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors" data-icon="keyboard\_arrow\_down">keyboard\_arrow\_down</span>

<h4 class="font-headline-md text-\[18px]">UI设计</h4>

</div>

<div class="col-span-2">

<span class="inline-flex items-center px-sm py-\[2px] bg-error/10 text-error rounded-full font-label-sm text-label-sm">高严重度</span>

</div>

<div class="col-span-3 text-on-surface-variant font-label-md text-label-md">

&#x20;                                   320 条评论 <span class="text-outline mx-xs">•</span> 28% 占比

&#x20;                               </div>

<div class="col-span-3 flex justify-end items-center gap-sm">

<span class="font-label-md text-label-md text-on-surface-variant">平均评分:</span>

<span class="font-headline-md text-\[18px] text-error">3.2</span>

</div>

</div>

</div>

<div class="accordion-content border-t border-outline-variant bg-surface-container-lowest p-lg">

<div class="overflow-x-auto">

<table class="w-full text-left border-collapse">

<thead>

<tr class="border-b border-outline-variant">

<th class="py-md font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">子问题</th>

<th class="py-md font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">数量</th>

<th class="py-md font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">情绪</th>

<th class="py-md font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">概述</th>

<th class="py-md font-label-md text-label-md text-on-surface-variant uppercase tracking-wider text-right">操作</th>

</tr>

</thead>

<tbody class="font-body-md text-body-md">

<tr class="border-b border-outline-variant hover:bg-surface-container transition-colors cursor-pointer group" onclick="toggleDetails('row1')">

<td class="py-md font-bold text-on-surface">按钮尺寸过小</td>

<td class="py-md font-mono-data text-mono-data">142</td>

<td class="py-md">

<span class="material-symbols-outlined text-error" data-icon="mood\_bad">mood\_bad</span>

</td>

<td class="py-md text-on-surface-variant max-w-xs truncate">用户发现在移动设备上很难点击主要操作按钮...</td>

<td class="py-md text-right">

<span class="inline-flex items-center px-sm py-\[2px] bg-secondary/10 text-secondary rounded-full font-label-sm text-label-sm">高置信度</span>

</td>

</tr>

<tr class="hidden bg-surface" id="row1">

<td class="p-xl" colspan="5">

<div class="grid grid-cols-1 lg:grid-cols-2 gap-xl">

<div class="space-y-md">

<div>

<p class="font-label-sm text-label-sm text-on-surface-variant uppercase mb-xs">深度分析</p>

<p class="text-on-surface">摩擦的核心源于移动端视口缺乏响应式的点击区域调整。在 iPhone 13 及更小的设备上，主要 CTA 按钮比苹果建议的 44px 点击目标小 28%。</p>

</div>

<div>

<p class="font-label-sm text-label-sm text-on-surface-variant uppercase mb-xs">建议方案</p>

<p class="text-on-surface">使用相对视口单位 (rem/em) 实施动态按钮内边距系统，并确保所有移动端交互的最小点击目标为 48px。</p>

</div>

</div>

<div class="space-y-md">

<div class="bg-surface-container-low p-md rounded-lg italic text-on-surface-variant relative">

<span class="material-symbols-outlined absolute -top-3 -left-1 text-primary-container opacity-20 text-\[48px]" data-icon="format\_quote">format\_quote</span>

&#x20;                                                           "按钮在我的 iPhone 13 上太小了。我填长表单时经常误触取消按钮而不是提交，这真的让人很沮丧。"

&#x20;                                                       </div>

<div class="flex flex-wrap gap-xs">

<span class="px-xs py-\[2px] border border-outline rounded text-label-sm">#移动端UX</span>

<span class="px-xs py-\[2px] border border-outline rounded text-label-sm">#无障碍</span>

<span class="px-xs py-\[2px] border border-outline rounded text-label-sm">#iPhone-13</span>

</div>

</div>

</div>

</td>

</tr>

<tr class="border-b border-outline-variant hover:bg-surface-container transition-colors cursor-pointer group">

<td class="py-md font-bold text-on-surface">对比度问题</td>

<td class="py-md font-mono-data text-mono-data">88</td>

<td class="py-md">

<span class="material-symbols-outlined text-tertiary" data-icon="sentiment\_neutral">sentiment\_neutral</span>

</td>

<td class="py-md text-on-surface-variant max-w-xs truncate">白色背景上的灰色文字不符合 WCAG 标准...</td>

<td class="py-md text-right">

<span class="inline-flex items-center px-sm py-\[2px] bg-secondary/10 text-secondary rounded-full font-label-sm text-label-sm">高置信度</span>

</td>

</tr>

</tbody>

</table>

</div>

</div>

</div>

<!-- Accordion Item 2 -->

<div class="tonal-layer-1 overflow-hidden opacity-80 accordion-item expanded">

<div class="flex items-center p-lg cursor-pointer hover:bg-surface-container-low transition-colors group" onclick="this.parentElement.classList.toggle('expanded')">

<div class="sentiment-bar bg-tertiary"></div>

<div class="grid grid-cols-12 gap-lg w-full items-center">

<div class="col-span-4 flex items-center gap-md">

<span class="material-symbols-outlined text-on-surface-variant" data-icon="keyboard\_arrow\_right">keyboard\_arrow\_right</span>

<h4 class="font-headline-md text-\[18px]">性能</h4>

</div>

<div class="col-span-2">

<span class="inline-flex items-center px-sm py-\[2px] bg-tertiary/10 text-tertiary rounded-full font-label-sm text-label-sm">中严重度</span>

</div>

<div class="col-span-3 text-on-surface-variant font-label-md text-label-md">

&#x20;                                   280 条评论 <span class="text-outline mx-xs">•</span> 24% 占比

&#x20;                               </div>

<div class="col-span-3 flex justify-end items-center gap-sm">

<span class="font-label-md text-label-md text-on-surface-variant">平均评分:</span>

<span class="font-headline-md text-\[18px] text-tertiary">3.5</span>

</div>

</div>

</div>

</div>

</section>

</div>

<!-- Footer -->

<footer class="flex justify-between items-center px-lg py-sm w-full bg-surface border-t border-outline-variant mt-auto">





</footer>

</main>

</div>

<!-- Floating Action Button -->

<div class="fixed bottom-xl right-xl z-50">

<button class="w-14 h-14 bg-primary text-on-primary rounded-full shadow-lg flex items-center justify-center hover:scale-110 active:scale-95 transition-all group relative">

<span class="material-symbols-outlined" data-icon="chat">chat</span>

<span class="absolute right-full mr-sm bg-inverse-surface text-inverse-on-surface px-md py-xs rounded-lg text-label-sm opacity-0 group-hover:opacity-100 whitespace-nowrap pointer-events-none transition-opacity">询问关于此报告的问题</span>

</button>

</div>

<script>

&#x20;       function toggleDetails(id) {

&#x20;           const el = document.getElementById(id);

&#x20;           if (el.classList.contains('hidden')) {

&#x20;               el.classList.remove('hidden');

&#x20;           } else {

&#x20;               el.classList.add('hidden');

&#x20;           }

&#x20;       }

&#x20;   </script>

</body></html>

