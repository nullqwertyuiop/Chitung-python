# Public Version of Chitung (Python)

This project aims to provide users with a lite and open version of Chitung.

## 七筒：开放版 (Python)
### - 基于Mirai框架的QQ机器人

本项目基于七筒开放版与七筒本体开发，由七筒爱好者 Nullqwertyuiop 维护，旨在为用户提供可于 Python 环境使用的开放版七筒插件。

## 已移植的功能
Chitung-python 已完成以下功能的移植：

- /funct
    - 插件位置：`chitung.help`
    - 可用范围：群聊
    - 仅已移植 v0.1.3 的 /funct 功能，v0.1.4 使用的动态生成待移植

- /discl
    - 插件位置：`chitung.help`
    - 可用范围：群聊

- /bummer
    - 插件位置：`chitung.lottery`
    - 可用范围：群聊
    - 使用注意：使用本功能需要将七筒设置为管理员

- /c4
    - 插件位置：`chitung.lottery`
    - 可用范围：群聊
    - 使用注意：使用本功能需要将七筒设置为管理员

- /winner
    - 插件位置：`chitung.lottery`
    - 可用范围：群聊

- OK Animal
    - 插件位置：`chitung.lovely_image`
    - 可用范围：群聊

- 求签
    - 插件位置：`chitung.fortune_teller`
    - 可用范围：群聊
    - 使用注意：
        - 由于随机函数算法不同，可能得出与官方版七筒不同的结果
        - 可能包含 Chitung-python 作者的恶趣味，如需保持和官方版七筒一致的使用效果，请注释 `chitung.fortune_teller` 的 `第 48 - 53 行`

- /bank
    - 插件位置：`chitung.bank`
    - 可用范围：群聊
    - **不建议卸载**

- /shuffle
    - 插件位置：`chitung.shuffle`
    - 可用范围：群聊
    - 使用注意：使用本功能需要将七筒设置为管理员

## 正在开发

### 正在移植的功能
- /set
    - 正在从 `Project. Null` 未删除源码重写

- /laundry
    - 正在从 `Project. Null` 未删除源码重写

- 兽设

- 奶茶

- 吃什么

- Pizza

- 意见反馈

- 掷骰子

- /fish
    - 将从 `Project. Null` 未删除源码重写

- /blackjack

- /roulette

### 正在进行的改进
- 支持设置最低群组人数

- 引入依赖注入
    - 群插件开关
    - 全局插件开关
    - 群组黑名单
    - 用户黑名单

- 支持热加载、卸载插件

- 支持私聊使用

## 部署使用

### 作为插件使用
若正在使用基于 Ariadne 框架开发的机器人，且已安装 Saya 及 GraiaScheduler 支持，可直接克隆本仓库并复制仓库中 `chitung` 文件夹至目标机器人的自定义插件目录

### 直接使用
<! Placeholder !>

### 特性
得益于本项目使用的插件管理器 Saya，用户可灵活控制机器人使用的插件。
#### 安装插件
##### 正在运行时卸载（热加载）
<! Placeholder !>
##### 已关闭时安装
直接将所需安装的插件文件或文件夹复制至 `chitung` 文件夹即可。
#### 卸载插件
##### 正在运行时卸载
<! Placeholder !>
##### 已关闭时安装
直接删除所需删除的插件目录即可，对应插件位置可于本须知 [已移植的功能](#已移植的功能) 中查看。

## 版权

### 美术素材
`以下内容与 Chitung-public 一致`

七筒绝非是他的城市里唯一的居民。开发者为七筒设计了形象的同时，也为钓鱼场老板、赌场老板、以及未来其他功能出现的角色设计形象。我们感谢如下艺术创作者赋予七筒世界里的形象帅气的外表。

- 七筒角色设计：[青蛙奥利奥](https://weibo.com/u/2843849155)

- 七筒头像：[青蛙奥利奥](https://weibo.com/u/2843849155)

- Maverick角色设计：[凹布瑞](https://weibo.com/u/5163824559)

- 里格斯先生角色设计：[凹布瑞](https://weibo.com/u/5163824559)

- 克莱因先生角色设计：[凹布瑞](https://weibo.com/u/5163824559)

- 七筒开放版图标：[苟砳砳](https://weibo.com/u/3095618097)

- 麻将牌图标：[维基百科-麻将](https://zh.wikipedia.org/wiki/%E9%BA%BB%E5%B0%86)

- 其他美术素材：由七筒开发组购买或者设计。

我们允许用户自由在使用七筒开放版时，修改上述非开源美术素材；允许基于上述形象进行二次创作；不支持用户在其他渠道流通这些非开源美术素材。

### 涉及项目

- 基于 AGPLv3 协议的 [Mirai](https://github.com/mamoe/mirai)

- 基于 AGPLv3 协议的 [Ariadne](https://github.com/GraiaProject/Ariadne)

- 基于 AGPLv3 协议的 [Chitung-public](https://github.com/KadokawaR/Chitung-public)

- Shibes as a service [Shibe.online]()

- DaaS(Dog-as-a-Service) [Dog.ceo]()

- Hello World, This Is Dog [random.dog]()
