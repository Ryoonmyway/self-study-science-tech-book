# 自学科学与技术：反内卷的大学生存工程学

一本写给大学生的期末生存手册：用工程的办法对付考试，从课业里“抢”出时间，去做自己真正想做的事。

作者：在路上的小凉（公众号：在路上的小凉；X：[@Ryo_onmyway](https://x.com/Ryo_onmyway)）

## 阅读

- **PDF**：在 [Releases](https://github.com/Ryoonmyway/self-study-science-tech-book/releases/latest) 下载最新版
- **在线**：直接阅读 [book.md](book.md)

## 目录

- 零，上学vs学习
- 一，平时工作
- 二，科目分诊：认清你的对手
- 三，概念：知识的无损压缩
- 四，内化：试卷的逆向工程
- 五，精准输出，指哪打哪
- 六，考场控制工程
- 七，大杀器：Agent交互学习
- 八，如果只有三天备考
- 九，最后的最后

书里第七章用到的复习工具在这里：[Exam Hacker](https://github.com/Ryoonmyway/exam-hacker)。

## 反馈

读完了？花两分钟告诉我哪里有用、哪里没用。下一版会根据这些反馈修改。

<img src="assets/feedback-qr.png" alt="读者反馈问卷二维码" width="240">

## 许可

本书采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans) 协议。欢迎转载和改编，请注明作者与原始地址，改编版本须沿用同一协议。

以下用途视为商业使用，未经许可不得进行：放进付费社群或付费课程，打包进收费资料包，以任何形式单独售卖。

## 构建

书稿在 Obsidian 里维护，`build.py` 负责同步 `book.md` 并生成 PDF：

```bash
pip install markdown pymupdf
python build.py
```

版本号默认取当天日期（例如 `20261017`），也可以用 `--version` 指定。PDF 输出到 `dist/`，不进仓库，发版时上传到 Releases。GitHub 会删掉附件文件名里的中文，上传时改用英文文件名、中文作显示名：

```bash
gh release upload <tag> "self-study-science-tech-<日期>.pdf#自学科学与技术-<日期>.pdf"
```
