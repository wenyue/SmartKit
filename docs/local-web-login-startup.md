# 本机 Web 服务的登录自启动

本功能只管理当前系统用户登录后的启动，不安装系统服务，不请求管理员权限，不启用 Linux lingering。自启动选择纳入现有按项目、Harness 和日期区分的每日检查；更新与维护决定先处理，自启动随后用一个独立的 Q 编号问题、A/B 选项和推荐理由阻塞询问。没有稍后或默认选项。

`runtime/local_web/__main__.py autostart status` 只读检查。`autostart enable` 与 `autostart disable` 分别保存明确的启用或拒绝决定，只有获得对应用户授权后执行。选择保存到当前用户的 Local Web 状态目录 `config.json` 的 `localWeb.autostart` 字段；缺失表示未询问，布尔值表示明确决定。其他用户的配置和启动项独立。多个项目仍分别经过自己的每日检查，但已保存的决定不重复询问。

Windows 使用当前用户 Startup 目录的快捷方式和 `pythonw.exe`。Linux 在用户 systemd 管理器可用时注册用户级 unit，否则在可识别的桌面环境使用 XDG Autostart。两种机制均不可用时报告不支持，不自行提权或修改系统级配置。系统级策略仍可能阻止登录触发；成功注册不等于已经实际观察过下一次登录。

启动项指向状态目录中的稳定启动器。每次受支持的会话 Hook 可以把已核验、未修改的运行入口更新到当前或更新的插件版本，不回退到旧版本，不重建用户禁用的系统项。插件目录不存在时启动器退出，不搜索任意缓存版本。配置、入口和注册文件的实际状态分别核验，不能把用户选择启用等同于注册成功。

原生注册未成功时，即使文件齐全，也保持未完成状态。失败保留已写入的明确选择和部分文件所有权，可通过再次明确启用重试或明确关闭清理；若所有权记录也失败，会同时报告两次失败并保留文件。未知或修改过的文件保留并报告。关闭仅移除已记录且内容未变的启动项及辅助文件，不停止现有聊天共用的 Web 进程。

卸载前使用 `autostart disable`。支持卸载回调的 Harness 可接入此操作；没有回调时不能保证宿主自动清理用户级启动项。此版本不增加虚构的跨 Harness 卸载事件。

原生命令格式参照 [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) 与 [Desktop Entry Exec](https://specifications.freedesktop.org/desktop-entry/latest/exec-variables.html)；两者采用各自的转义规则。
