"""Keep page content and navigation intact across presentation changes."""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_web.apps import diff, status


class Document(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.tags = []
        self.text = []
        self.feed(content.decode("utf-8"))

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class WebPageTests(unittest.TestCase):
    def test_readiness_preserves_all_outcomes_and_escapes_record_content(self):
        hostile = '<img src=x onerror="alert(1)"> & 中文'
        projects = []
        for outcome in ("passed", "findings", "failed", "unavailable"):
            projects.append({"project": hostile, "harness": "codex", "readiness": {
                "status": outcome, "message": hostile,
                "findings": [{"tool": hostile, "message": hostile, "guidance": hostile}],
            }})
        document = Document(status.render_application("readiness", "private & key", {"projects": projects}))
        text = "".join(document.text)
        for label in ("检查通过", "存在待处理发现", "检查失败", "证据不可用", "采集时间：未知", hostile):
            self.assertIn(label, text)
        self.assertFalse(any(tag in ("img", "script", "button") for tag, _ in document.tags))
        links = [attrs for tag, attrs in document.tags if tag == "a"]
        self.assertEqual([item["href"] for item in links], [
            "/readiness/?key=private%20%26%20key", "/setup/?key=private%20%26%20key"])
        self.assertEqual(links[0]["aria-current"], "page")
        self.assertNotIn("aria-current", links[1])

    def test_setup_keeps_missing_baselines_failures_and_migration_meanings(self):
        projects = []
        for outcome in ("initialized", "uninitialized", "baseline-required", "failed"):
            projects.append({"project": "D:/project", "setup": {
                "status": outcome, "message": "<read failure>",
                "setup_version": "1.2.20" if outcome == "initialized" else None,
                "plugin_version": "1.2.21", "migrations": [
                    {"version": "1.2.21", "guide": "references/<guide>.md"}],
            }})
        document = Document(status.render_application("setup", "key", {"projects": projects}))
        text = "".join(document.text)
        for label in ("已有设置基线", "尚未初始化", "缺少已完成设置的版本基线", "状态读取失败",
                      "未建立", "<read failure>", "声明的必要迁移", "可供设置流程评估的迁移声明",
                      "references/<guide>.md", "1.2.20", "1.2.21"):
            self.assertIn(label, text)
        self.assertFalse(any(tag in ("guide", "read", "script", "button") for tag, _ in document.tags))
        links = [attrs for tag, attrs in document.tags if tag == "a"]
        self.assertEqual(links[1]["aria-current"], "page")
        projects[0]["setup"]["migrations"] = []
        content = status.render_application("setup", "key", {"projects": projects[:1]})
        self.assertIn("当前没有适用的迁移声明。", content.decode("utf-8"))
        for feature in ("setup", "readiness"):
            empty = status.render_application(feature, "key", {"projects": []})
            self.assertIn("尚无项目记录。", empty.decode("utf-8"))

    def test_diff_keeps_manual_fallbacks_and_escapes_file_context(self):
        target = diff.Target(Path("D:/project & 中文"), 'src/a & "quoted".py', "blob:" + "a" * 40,
                             "https://github.com/o/r/pull/1/files")
        for automatic in (True, False):
            document = Document(diff.render_open_page(target, automatic=automatic))
            self.assertIn(target.path, "".join(document.text))
            links = [attrs["href"] for tag, attrs in document.tags if tag == "a"]
            self.assertEqual(links, [target.url(html_only=True), target.github])
            buttons = [attrs for tag, attrs in document.tags if tag == "button"]
            self.assertEqual(len(buttons), 1)
            self.assertEqual(buttons[0]["id"], "open")
            self.assertTrue(any(tag == "p" and attrs.get("role") == "status" for tag, attrs in document.tags))


if __name__ == "__main__":
    unittest.main()
