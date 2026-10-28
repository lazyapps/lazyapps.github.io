import AppKit
import QuartzCore

final class CaptureActions: NSObject {
    var window: NSWindow!
    private var dark = false
    @objc func change(_ sender: AnyObject) {}
    @objc func toggleAppearance() {
        dark.toggle()
        let appearance = NSAppearance(named: dark ? .darkAqua : .aqua)
        NSApp.appearance = appearance
        window.appearance = appearance
        window.contentView?.needsDisplay = true
        window.makeFirstResponder(nil)
    }
}

final class PreviewWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}

@main enum Capture {
    static func main() {
        let language = Bundle.main.object(forInfoDictionaryKey: "CaptureLanguage") as! String
        UserDefaults.standard.set([language], forKey: "AppleLanguages")
        precondition(L10n.language == language, "Preview language mismatch")
        let app = NSApplication.shared
        app.setActivationPolicy(.regular)
        app.appearance = NSAppearance(named: .aqua)
        let actions = CaptureActions()
        let menu = NSMenu()
        let root = NSMenuItem()
        let applicationMenu = NSMenu()
        let toggle = NSMenuItem(title: "Toggle Appearance", action: #selector(CaptureActions.toggleAppearance), keyEquivalent: "t")
        toggle.target = actions
        applicationMenu.addItem(toggle)
        applicationMenu.addItem(NSMenuItem(title: "Quit Preview", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        root.submenu = applicationMenu
        menu.addItem(root)
        app.mainMenu = menu
        let window = PreviewWindow(contentRect: NSRect(origin: .zero, size: ControlPanelView.preferredSize), styleMask: .borderless, backing: .buffered, defer: false)
        window.title = "Doze preview · \(language)"
        window.appearance = NSAppearance(named: .aqua)
        let action = #selector(CaptureActions.change(_:))
        let panel = ControlPanelView(target: actions, automaticAction: action, delayAction: action, loginAction: action, primaryAction: action, awakeAction: action, quitAction: action)
        // Match the native popover's horizontal safe area in the borderless preview.
        panel.additionalSafeAreaInsets = NSEdgeInsets(top: 0, left: 13, bottom: 0, right: 13)
        window.contentView = panel
        actions.window = window
        panel.update(notice: nil, automatic: true, delay: .tenMinutes, login: true,
                     actionTitle: L10n.string("action.dim"), actionEnabled: true, mediaActive: true)
        window.center()
        window.makeKeyAndOrderFront(nil)
        app.activate(ignoringOtherApps: true)
        app.run()
    }
}
