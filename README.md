小米运动（Zepp Life）自动刷步数（邮箱/手机号通用版）- Github Actions 部署指南

一、部署步骤

1. Fork 仓库

访问目标Github仓库，点击右上角「Fork」，将仓库复制到自己的Github账号下。

2. 配置账号密码（关键）

①. 进入Fork后的仓库，点击「Settings → Secrets and variables → Actions → New repository secret」；

②. 按以下格式添加2个必填Secret变量：
Secrets 名称 填写内容说明 
USER Zepp Life登录账号（支持两种格式：① 邮箱账号 ② 手机号账号，非小米账号，需是Zepp Life独立账号） 
PWD Zepp Life账号对应的登录密码 

3. 手动触发运行（首次必做）

1. 仓库页面点击「Actions」；

2. 左侧选择「刷步数」 workflow；

3. 点击「Run workflow」，即可触发首次刷步数任务。

二、可选配置：自定义运行时间

若需修改默认运行时间，编辑仓库中的 .github/workflows/run.yml 文件：

• 找到 cron 语句，按 UTC时间 配置（北京时间 = UTC时间 + 8小时）；

• 示例：北京时间19点对应UTC时间11点，cron配置为 0 11 * * *。

三、注意事项

1. 默认运行时间：每天UTC时间11点（北京时间19点），由 run.yml 中的cron规则控制；

2. 支付宝步数同步问题：若支付宝未更新步数，需重新操作「Zepp Life → 设置 → 账号 → 注销账号 → 清空数据」，再重新登录并绑定支付宝；

3. 步数更新说明：小米运动（Zepp Life）App内不会显示刷取的步数，仅关联的第三方（如支付宝）会同步更新；

4. 账号区分：务必使用「Zepp Life独立账号」（邮箱/手机号均可），而非「小米账号」，否则无法正常登录；

5. 手机号账号注意：需使用注册Zepp Life时绑定的手机号，若之前用手机号绑定过小米账号，需确认是Zepp Life独立登录账号（而非通过小米账号授权登录）。
