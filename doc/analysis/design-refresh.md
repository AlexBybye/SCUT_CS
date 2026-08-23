# 前端 UI 重塑（design/ui-refresh）设计说明

> 探索分支：`design/ui-refresh`（独立于 master，未带入 master 正在进行的语料校验改动）
> 范围：SCUT 老学长 `apps/scut-senior/web` 前端

## 0. 设计 Read 与三档

- **页种**：产品级 UI（AI 学习工作台：会话记录 + 输入条 + 个人中心），非营销落地页。
- **受众**：华南理工计院学生，工具、可信、不喧哗，但也需要「老学长」的书卷气质而非「AI 蓝渐变」的通用感。
- **气质**：砚台与宣纸——暖调宣纸底色、墨色文字、单一品牌强调色（靛青为主，朱砂可选）。
- **三档**：`DESIGN_VARIANCE 4`（产品 UI 要可预期）、`MOTION_INTENSITY 5`（靠 CSS 流体的进出场/悬停反馈）、`VISUAL_DENSITY 6`（信息密度高的工具）。

因这是 **产品 UI / 工作台**（skill 第 13 节「Out of Scope」所定义的「非营销页」），本说明只把该 skill 中适用于产品面（令牌、动效、分组、可发现性、对比度、减少动态）的部分落地到各表面，不把营销页规则硬套进聊天界面。

---

## 1. 痛点与对应解法

| 用户反馈 | 根因 | 解法 |
|---|---|---|
| 个人中心「插件表」过长 | `PluginRegistryPanel` 把 55 门课程插件 + 预置 + 工具全部平铺堆叠卡片，一路滚到底 | 三组改为**可折叠分组**；课程组默认展开但**限高内滚 + 搜索**；装载态上浮 |
| 课程选择「又长又宽、行数多」 | 原生 `<select>` 装载 55 门课程，每项还带长可用性说明，且无搜索/分组 | 自研**可搜索下拉 `OptionPicker`**：触发钮只显示课程名 + 状态点；面板内搜索、分组、限高、键盘导航 |
| 「AI 味重、缺主题配色与动效」 | 冷灰 + 泛蓝底 + `#2b5fbe` 泛蓝强调色；无主题性格、无动效层 | 主题令牌重写 + 双品牌强调色 + 统一动效令牌 + 组件进出场动效 |

---

## 2. 主题系统（`styles.css`）

### 2.1 新配色：砚台与宣纸
- **中性底**由冷灰改为**暖调宣纸**：亮色 `--page:#f4f2ec / --panel:#faf8f3 / --raised:#fff / --sunken:#ebe7dd`；暗色为深墨 `#14171c / #1b1f26 / #232830 / #0f1216`。
- **文字**用心形墨色（非纯黑）：亮 `#221f19`、暗 `#e9ecef`；三级 muted/soft 均由它派生。
- **圆角**统一为一套并略微放大：`--r-xs 4px / --r-sm 6px / --r-md 12px`，去掉 pill 与随意值。
- **阴影**由纯黑投影改为**带色相的柔和阴影**（亮色暖、暗色冷）。

### 2.2 双品牌强调色（可切换）
全站只有一个强调色语义 `--accent`，但允许在两套品牌色间切换，由 `<html data-accent="indigo|vermilion">` 控制：

- **靛青 indigo（默认）**：亮 `#3a5a8c`、暗 `#93aede`。书卷、可信、安静。
- **朱砂 vermilion（可选）**：亮 `#a83b22`、暗 `#dd8a72`。热忱、有辨识度，像一枚印章。

两套色各自在亮/暗下都重写了 `--accent / --accent-hover / --accent-wash / --accent-on / --focus`，确保按钮文字对比度在两种主题下都过 WCAG AA（白色高对比文字放在深的强调底上）。语义色 ok / warn / bad 独立保留，且与朱砂强调色刻意区分（bad 用玫红而非橙红），避免破坏性操作读成「主按钮」。

### 2.3 动效令牌
- `--ease-out: cubic-bezier(0.16,1,0.3,1)`、`--ease-spring: cubic-bezier(0.22,1,0.36,1)`（非线性，非匀速）。
- `--dur-fast 120ms / --dur 200ms / --dur-slow 320ms`，各组件统一引用，不再各写各的时长。
- 全局 `prefers-reduced-motion` 兜底：把动画/过渡时长压到接近 0，实现「减弱动态」降级。

---

## 3. 组件改动明细

### 3.1 新增 `components/OptionPicker.vue`（核心）
用自研 combobox 替换课程/模型/Workflow 的原生 `<select>`。要点：

- **触发钮**：只显示当前值 + 可选状态点 + caret；`role="combobox"` + `aria-expanded`，兼容 `disabled` 态。
- **面板**：`<Teleport to="body">` + `position: fixed`，JS 按按钮锚点计算并**钳制在视口内**；默认**向上弹出**（composer 贴在底部）。宽度 `220–320px`，内容限高内滚。
- **搜索**：按 label / hint 过滤；可搜索时开面板即聚焦搜索框。
- **分组**：可传入 `group`，未搜索时渲染组头；搜索时拍平。
- **键盘**：↑↓ 移动高亮（跳过禁用）、Enter 选中、Esc 关闭、Home/End 到头/尾；触发钮展开后方向键同样可移动高亮（没有搜索框也能键盘操作）。
- **ARIA**：`listbox` / `option` / `aria-selected` / `aria-disabled`。
- **状态点**：`ok`（可用）/ `warn`（仅 Fixture，用于课程）/ `accent`。
- 弹出动画用 `op-pop`（淡入 + 轻微位移），并随 reduced-motion 关闭。

定位实现刻意**不依赖面板高度测量**——只为按钮锚点取 `top/bottom` 并给 `max-height`，避免「面板未渲染时就测高」导致永不显示的 bug，同时没有布局闪烁。

### 3.2 `components/Composer.vue`
- 两处原生 `<select>`（课程、模型）与 Workflow 一并换成 `OptionPicker`，并构建面向它的 options：
  - **课程**：`label=课程名`、`hint=可用性描述`、`disabled=!selectable`、`dot`（可加载=ok / 仅 Fixture=warn）、`group`（可选用 / 暂不可用）。55 门不再撑出一条超宽超长的原生下拉。
  - **模型**：`label=公司 · 名称（Preview）`、`hint=计费 · 状态`、`group`（可选 / 暂不可选）。
  - **Workflow**：固定五项，`searchable=false`。
- 处理加载/空态 placeholder 与禁用（课程加载中、模型目录加载失败、运行中均禁用）。
- 配置条样式改为针对 `.op` / `.op-trigger` 收窄（只显示当前值、宽度上限、多档响应式压缩）。
- 抽屉展开用 `drawer-pop`（淡入 + 上移）。

### 3.3 `components/PluginRegistryPanel.vue`
- 三组（课程插件 / Agent Preset / 受控工具）各改为**可折叠 `group-toggle` 头**（chevron 旋转），默认：课程组展开、预置/工具收起。
- **课程组**：新增搜索框（按课程名或 course_id 过滤）+ 清单 `max-height:300px` 内滚，装载的课程浮到最前，让所有 55 门都在一屏内可搜、可滚，不再把面板撑成无限长。
- 组头带 `计数 chip`，课程组额外显示「已装载 N」。
- 修正了两处既有 bug：`.btn-ghost`（从未定义，改用全局的 `.btn-quiet`）与 `var(--surface)`（不存在，改为 `var(--raised)`）。

### 3.4 `components/AssistantSettingsPanel.vue`
- 新增**品牌色选择器**（`role="radiogroup"`）：靛青 / 朱砂两枚色卡单选，选中态以强调色环高亮，绑定 `store.accentTheme`。与既有三档明暗滑块相互独立。
- 明暗滑块、品牌色选择都走 `themePreference` 持久化。

### 3.5 `src/themePreference.ts`
- 新增强调色偏好轴：
  - `AccentTheme = "indigo" | "vermilion"`，`DEFAULT_ACCENT = "indigo"`；
  - `ACCENT_STORAGE_KEY`（`scut_senior_assistant_accent`）独立持久化；
  - `parseAccentTheme` 大小写不敏感、脏数据回退默认靛青；
  - `applyAccent` 落到 `<html data-accent>`。
- 与既有明暗模式轴相互独立、互不影响存储键。

### 3.6 `composables/useAppStore.ts`
- 新增 `accentTheme` ref（读取 localStorage、应用 `<html data-accent>`、watch 写回）与 `setAccentTheme` 收口写入，并在返回对象中暴露。

### 3.7 `components/AppTopBar.vue` + `AccountMenu.vue`
- 个人中心浮层包一层 `<Transition name="menu-pop">`，右上锚点的弹入/弹出动效（上移 + 缩放），随 reduced-motion 关闭。

### 3.8 跨组件一致性修复
- `MaterialContributionPanel.vue`：删除局部硬编码 `#b42318`（改走 `--bad-text`）、`#8a6100`（改走 `--warn-text`），并修 `--surface` bug。
- 其余组件（WorkflowResult / ConversationRail / TranscriptPanel / WorkflowDrawer / ByokCredentialsPanel）均只消费令牌，未硬编码颜色，天然跟随新主题。

---

## 4. 验证

- `npm run typecheck`：通过。
- `npm test`：15 个测试文件、**103 例全绿**（新增 5 例强调色偏好测试，原 98 例未回退）。
- `npm run build`（typecheck + vite build）：通过。
- 本地 mock API（`/api/v1/*` 默认 mock）已启动，`/me` `/models`(6) `/courses`(55) `/plugin-registry` 均返回 200；运行于 5173 的 Vite 已验证编译 `OptionPicker.vue` / `Composer.vue` 无报错并热更新。
- 建议人工在浏览器复核：亮/暗 × 靛青/朱砂四套主题、课程/模型可搜索下拉、个人中心插件分组折叠与课程搜索、窄屏响应式。

## 5. 分支与提交

本分支仅含 `apps/scut-senior/web` 与 `doc/analysis/design-refresh.md` 的改动；master 上未提交的 `corpus_validator.py` 等语料校验改动**未纳入**本分支提交。
