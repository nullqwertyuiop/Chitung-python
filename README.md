# Public Version of Chitung (Python)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/08a8c365dd25419b811b0b77435c46ec)](https://app.codacy.com/gh/nullqwertyuiop/Chitung-python?utm_source=github.com&utm_medium=referral&utm_content=nullqwertyuiop/Chitung-python&utm_campaign=Badge_Grade_Settings)
[![CodeQL](https://github.com/nullqwertyuiop/Chitung-python/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/nullqwertyuiop/Chitung-python/actions/workflows/codeql-analysis.yml)
![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)

This project aims to provide users with a lite and open version of Chitung.

## 七筒：开放版 (Python)

### - 基于Mirai框架的QQ机器人

本项目基于七筒开放版与七筒本体开发，由七筒爱好者维护，旨在为用户提供可于 Python 环境使用的开放版七筒插件。

## 已移植的功能

Chitung-python 已完成以下功能的移植：

- /funct
    - 插件位置：`chitung.help`
    - 可用范围：群聊
    - 仅已移植 v0.1.3 的 /funct 功能，v0.1.4 使用的动态生成待移植

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
        - 可能包含 Chitung-python 作者的恶趣味，如需保持和官方版七筒一致的使用效果，请注释 `chitung.fortune_teller` 中 `random.seed(...)` 下的第一个 `if` 代码块

- /bank
    - 插件位置：`chitung.bank`
    - 可用范围：群聊
    - 附属功能：`/laundry` `/set`
    - **不建议卸载**

- /shuffle
    - 插件位置：`chitung.shuffle`
    - 可用范围：群聊
    - 使用注意：使用本功能需要将七筒设置为管理员

- /adminhelp
    - 插件位置：`chitung.utils`
    - 可用范围：群聊

- /num
    - 插件位置：`chitung.utils`
    - 必要参数：`-g`或`-f`
    - 可用范围：群聊

- /coverage
    - 插件位置：`chitung.utils`
    - 可用范围：群聊

- 复读
    - 插件位置：`chitung.repeater`
    - 可用范围：群聊

- /dice
    - 插件位置：`chitung.dice`
    - 可用范围：群聊
    - 附属功能：`.d1` `.1d1`

- /fish
    - 插件位置：`chitung.fish`
    - 可用范围：群聊
    - 附属功能：`/endfish` `/collection` `/fishhelp` `/handbook`

- 黑名单
    - 组件位置：`chitung.utils.blacklist`
    - 生效范围：全局、好友、群聊
    - **不可卸载**

## 正在开发

### 正在移植的功能

- Responder

- UniversalResponder

- 兽设

- 奶茶

- 吃什么

- Pizza

- 意见反馈

- 掷骰子

- /blackjack

- /roulette

- 骰宝

### 正在进行的改进

- 支持设置最低群组人数

- 引入依赖注入
    - 群插件开关
    - 全局插件开关

- 支持热加载、卸载插件

- 支持私聊使用

## 部署使用

### 作为插件使用

若正在使用基于 `Ariadne` 框架开发的机器人，且已安装 `Saya` 及 `GraiaScheduler` 支持，可直接克隆本仓库并复制仓库中 `chitung` 文件夹至目标机器人的自定义插件目录

### 直接使用

<! Placeholder !>

### 特性

得益于本项目使用的插件管理器 Saya，用户可灵活控制机器人使用的插件。

<! Placeholder !>

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