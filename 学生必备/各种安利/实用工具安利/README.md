> 主要是我平时会用到、或者觉得值得留在收藏夹里的工具。以 Windows 为主，也放了几款跨平台的。链接尽量给项目 GitHub 或官网，第三方下载站就省了。发现链接挂了、功能变了，欢迎提 PR 修正。

电脑用久了，总会碰到几件烦心事。卸个软件还得跟残留斗智斗勇，合并几份 PDF 居然要上传网站，手机传张照片非得先发给自己。打游戏闪退了，更是全靠猜，散热还是驱动？

## 🧹 软件安装、卸载与系统整理

### GeekUninstallerToolModded

[MLChinoo/GeekUninstallerToolModded](https://github.com/MLChinoo/GeekUninstallerToolModded) · Windows · **非官方修改版**

系统刚重装完还好，过一个学期再看软件列表，往往能翻出一堆“当时只是试一下”的东西。这版 Geek Uninstaller 可以批量卸载、清理残留。遇到卸载入口坏掉的程序，也能试着进一步清理。强制删除前，先看一眼目录和组件有没有被别的软件共用。

仓库 README 明写了修改商业软件二进制文件、破解授权和屏蔽更新。运行这个版本，授权合规和程序安全的风险得自己承担。链接留着供了解，真想一次卸一堆软件，我会用下面的 BCU。至于老电脑卡顿，卸掉几个软件也不会让它原地复活。

### Bulk Crap Uninstaller（BCU）

[BCUninstaller/Bulk-Crap-Uninstaller](https://github.com/BCUninstaller/Bulk-Crap-Uninstaller) · Windows · 免费开源

名字挺不客气，做的事倒很实在。换电脑或者清理旧环境时，可以把一批软件勾起来一起卸，省得挨个打开卸载器。它支持不少 Windows 常见的软件安装形式，也能扫描残留、找出部分孤立条目。

清单里名字陌生的东西先别勾。运行库、驱动组件、学校教学软件的依赖，看着不起眼，用到的时候缺一个都够折腾。清残留也先看路径。

### UniGetUI

[Devolutions/UniGetUI](https://github.com/Devolutions/UniGetUI) · Windows 优先，也提供其他平台构建 · 免费开源

电脑上有几十个软件，一个个去官网检查更新，未免太有仪式感。UniGetUI 给 WinGet、Scoop 等包管理器套了个图形界面，搜索、安装、更新和卸载都在一个窗口里。重装系统后装回常用软件，或者隔一阵统一更新一次，都省事。

能搜到什么取决于软件源，第三方包也可能由别人打包。碰到名字相似、来源陌生的包，先核对发布者。项目现在由 Devolutions 维护，下载走上面的仓库。项目已经提醒过，有些同名域名看着像官网，别信。

### Dism++

[Chuyu-Team/Dism-Multi-language](https://github.com/Chuyu-Team/Dism-Multi-language) · Windows · 系统维护

Windows 更新几轮之后，C 盘空间经常莫名其妙少一截。Dism++ 把空间回收、更新组件管理、启动项和系统镜像操作放进了图形界面，知道自己要动哪一项的时候，用它比到处找命令方便。

只是删临时文件，Windows 自带的“存储感知”通常就够了。要动驱动、系统组件、Appx 或其他底层配置，先弄懂选项，留个还原点或备份。下载顺着项目给的渠道找，搜到个“Dism++ 绿色加强版”就直接运行，多少有点太勇敢了。

### Czkawka

[qarmin/czkawka](https://github.com/qarmin/czkawka) · Windows / macOS / Linux · 免费开源

硬盘里到底有多少份“最终版（3）”？课程资料、截图、照片和备份压缩包攒久了，一个文件在三个目录里各躺一份也不稀奇。Czkawka 能找重复文件、相似图片和空目录，适合先扫一遍下载文件夹、图片库和旧备份。

第一次用，扫完先预览。两张图相似，可能恰好就差你想留的那一处。几份备份该留哪份，也得自己看。

## 📄 文档、截图与文件传输

### ONLYOFFICE Desktop Editors

[ONLYOFFICE Desktop Editors 官网](https://www.onlyoffice.com/download-desktop) · Windows / macOS / Linux · 免费桌面版

要是平时就写写课程报告、改表格、做 PPT，ONLYOFFICE 的界面和常见的 Office 操作习惯挺接近。DOCX、XLSX、PPTX 可以在本地离线编辑，文档里也能加评论、开修订。

普通作业和报告用起来比较顺手。手里有带复杂 VBA 的文件、特殊排版或大型 Excel 模型，先拿实际文件试一下兼容性。需要实时多人协作的话，还得配在线服务。

### Stirling-PDF

[Stirling-Tools/Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) · 自托管 / 桌面端 · 开源核心，部分功能商业化

把三份 PDF 合成一份、删几页、压缩一份扫描件，本来都是小事。偏偏搜出来的网站经常写着“免费试用，导出请登录”。Stirling-PDF 可以在本地或自己部署的环境里做这些事，也能转格式、跑 OCR、加水印和做脱敏。经常整理课件、论文附件的，可以用工作流或 API 批量跑，或者接进自己的工具链。

要逐字改正文、逐页做排版，得用专门的 PDF 编辑器。合同审批和资料归档也得另找工具。自己部署时，更新、访问权限和数据保存都得自己管，具体功能和授权看你用的版本。

### ShareX

[ShareX/ShareX](https://github.com/ShareX/ShareX) · Windows · 免费开源

Windows 自带的截图快捷键已经挺好用。写 bug 反馈或者实验报告时，麻烦的是截完还要画箭头、标序号、打码，有时还得录个 GIF 给同学看。ShareX 能滚动截图、录屏和标注，也能把这些操作接起来，最后存进指定文件夹。

上传可以关。截学校或工作内部页面前，先看一下自动上传的设置，发出去之前再瞄一眼有没有漏掉学号、账号或 Token。

### LocalSend

[localsend/localsend](https://github.com/localsend/localsend) · Windows / macOS / Linux / Android / iOS · 免费开源

手机上的照片要传到电脑，很多人的第一反应还是打开聊天软件，“发送给自己”。用 LocalSend，两台设备在同一个能互通的局域网里，就可以直接传文件和文本，省了登录和上传网盘。手机和电脑用的系统不一样也没关系。

换了网络、设备搜不到时，先看局域网有没有隔离设备，或者是不是防火墙挡住了。它做的是局域网传输，隔着公网传文件得另找办法。这份清单里，要我给不怎么折腾电脑的同学推荐一款，我多半会先说它。

## 🪟 Windows 日常效率

### Microsoft PowerToys

[microsoft/PowerToys](https://github.com/microsoft/PowerToys) · Windows · 微软官方开源

这里面有一半功能，Windows 本来就该自带。VS Code、浏览器、文档和终端一起开的时候，我会先试 FancyZones，省得每次重新拖窗口。批量改文件名有 PowerRename，想复制截图里的字有 Text Extractor，另外还有图片缩放和键盘快捷键工具。

用到哪项开哪项就行。快捷键跟 IDE 或输入法撞了，改掉那个组合键。指望它给游戏加帧数就想多了。

### Flow Launcher

[Flow-Launcher/Flow.Launcher](https://github.com/Flow-Launcher/Flow.Launcher) · Windows · 免费开源

习惯敲两个字就打开软件的人，可以试试 Flow Launcher。快捷键叫出一个搜索框，能开应用、找文件、算个数，也能跑一些命令。想搜更多东西，可以装插件，先看看是谁做的、会用到什么权限。

文件没进索引，搜索框里就未必找得到。要在目录间来回翻，文件管理器照样用得上。它可以和 PowerToys 一起用，快捷键或启动器功能撞了，留自己顺手的那个就行。别把“管理效率工具”也变成一项工作。

## 🌐 网络连接与校园生活

### drcom4scutGUI

[AlexBybye/drcom4scutGUI](https://github.com/AlexBybye/drcom4scutGUI) · 华南理工大学校园网

这款挺有地域限制，放在 SCUT_CS 里倒正合适。宿舍校园网掉线一次就得再认证一次，来回几趟是真的烦。它给 Dr.COM 校园网认证做了图形界面，可以配账号、做有线认证。项目文档也写了怎么自动连接、断线重连，以及支持哪些校园网页认证场景。Windows、macOS、Linux 的用法都能在 README 里找到。

它省的是重复登录的工夫。带宽和计费照学校的规则走，认证服务器出故障或者网络环境不匹配，换个界面也解决不了。其他学校的同学先核对自己的认证方式。

### Clash Verge Rev

[clash-verge-rev/clash-verge-rev](https://github.com/clash-verge-rev/clash-verge-rev) · Windows / macOS / Linux · Tauri 客户端

原版 Clash Verge 停更后，这个社区续作接过了图形客户端的活。手头已有兼容的代理配置或订阅，可以在同一个界面里管理订阅、切策略组、设分流规则，换个桌面系统也不用重新习惯一套操作。

**客户端不提供节点或订阅。** 订阅失效、服务质量差或者规则配错了，还是得查各自的原因。项目以前出过和系统服务有关的本地提权问题，尤其是 Windows 用户，记得用已修复的版本，谨慎开启高权限服务。下载认准项目发布页或它明确指向的渠道，“整合免配置版”就算了。

## 🧯 硬件排障与重装救急

### HWiNFO

[HWiNFO 官网](https://www.hwinfo.com/) · Windows · 个人使用有免费版本

游戏突然掉帧、风扇狂转，先别靠摸出风口猜。HWiNFO 能看 CPU、GPU 等硬件的温度、频率、功耗和传感器状态，也能记 CSV 日志。回头对一下卡顿发生的时间，看看有没有撞上 CPU 温度限制、GPU 功耗异常，多少能找到点线索。

排障还得自己动手。有些传感器读数不一定拿得到，拿到了也未必和外部仪器的测量值一致。只看一次最高温度，定不了故障原因。还有个容易误会的地方，免费版部分共享内存接口有连续使用时限，主要影响外部集成或 Overlay。监控窗口本身可以继续用。

### Display Driver Uninstaller（DDU）

[Wagnard/display-drivers-uninstaller](https://github.com/Wagnard/display-drivers-uninstaller) · [Wagnardsoft 官网](https://www.wagnardsoft.com/) · Windows

驱动反复装不上，或者换了显卡品牌，怀疑旧驱动残留在捣乱，这时候可以考虑 DDU。它能深度清理 NVIDIA、AMD、Intel 显卡驱动和相关残留。通常先备份、备好新驱动，再按官方说明进安全模式操作。清完以后，新驱动还得自己装。

正常更新驱动用不着每次跑一遍。显卡硬件、供电或散热有问题，也得顺着故障另查。

### Ventoy

[ventoy/Ventoy](https://github.com/ventoy/Ventoy) · Windows / Linux · 启动盘工具

每试一个 Linux 发行版就重做一遍启动盘，折腾几次就烦了。U 盘装好 Ventoy 后，可以把几个受支持的 ISO 直接复制进去，开机从菜单里选。Windows 安装盘、Linux 镜像和一些维护工具能放在同一支 U 盘里。

镜像和电脑固件都有兼容性差异。**首次把 Ventoy 装到 U 盘上可能清掉目标盘的数据**，动手前核对盘符，别把存资料的移动硬盘选进去。要保住原有数据，先另外备份。

## 📌 怎么选，没必要全装

想挑几款平时就用得上的，可以先看 LocalSend、PowerToys、UniGetUI 和 ONLYOFFICE。实验报告写得多、截图和 PDF 攒得快，再加 ShareX 和 Stirling-PDF。攒了一堆软件要卸，先用 BCU。要清的是重复文件，再开 Czkawka。

Dism++、DDU、HWiNFO 和 Ventoy，遇到具体问题再翻出来就行。华工校园网和代理客户端也各有用得上的场合。收藏夹里躺着几个工具，通常比电脑里又多出一批“当时只是试一下”的软件划算。