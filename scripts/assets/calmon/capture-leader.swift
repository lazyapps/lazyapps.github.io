// Render the current native LeaderHelpView without starting calmon's window manager.
import AppKit
import CoreText

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
CTFontManagerRegisterFontsForURL(URL(fileURLWithPath: CommandLine.arguments[2]) as CFURL, .process, nil)
precondition(PixelFace.tiny5.fontCount == 1 && PixelFace.panel.fontCount == 2, "All native pixel fonts must load before capture")
Ink.accent = Accent.green.color
let help = LeaderHelpView()
help.sections = LeaderCommand.help(labels: JumpSettings.defaults.keys(layout: [:]), layout: [:])
help.frame = CGRect(origin: .zero, size: help.intrinsicContentSize)
let panel = NSView(frame: help.bounds.insetBy(dx: -24, dy: -24))
panel.wantsLayer = true
panel.layer?.backgroundColor = NSColor.black.cgColor
help.setFrameOrigin(CGPoint(x: 24, y: 24))
panel.addSubview(help)
panel.layoutSubtreeIfNeeded()
let bitmap = panel.bitmapImageRepForCachingDisplay(in: panel.bounds)!
panel.cacheDisplay(in: panel.bounds, to: bitmap)
try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))

if CommandLine.arguments.count > 3 && !CommandLine.arguments[3].hasPrefix("-") {
    let image = OnboardingKeyPanel.image(settings: .defaults, keyboard: [:], scale: 2)!
    let representation = NSBitmapImageRep(data: image.tiffRepresentation!)!
    try representation.representation(using: .png, properties: [:])!
        .write(to: URL(fileURLWithPath: CommandLine.arguments[3]))
}

if CommandLine.arguments.count > 4 && !CommandLine.arguments[3].hasPrefix("-") {
    let symbols = ["safari", "doc.text", "terminal", "envelope", "calendar", "gearshape", "apple.logo", "wifi", "battery.100"]
    let sprite = NSImage(size: NSSize(width: symbols.count * 24, height: 24))
    sprite.lockFocus()
    for (index, name) in symbols.enumerated() {
        let symbol = NSImage(systemSymbolName: name, accessibilityDescription: nil)!
            .withSymbolConfiguration(.init(pointSize: 16, weight: .medium))!
        let scale = min(18 / symbol.size.width, 18 / symbol.size.height)
        let size = NSSize(width: symbol.size.width * scale, height: symbol.size.height * scale)
        symbol.draw(in: NSRect(x: CGFloat(index * 24) + (24 - size.width) / 2,
                              y: (24 - size.height) / 2, width: size.width, height: size.height))
    }
    sprite.unlockFocus()
    let representation = NSBitmapImageRep(data: sprite.tiffRepresentation!)!
    try representation.representation(using: .png, properties: [:])!
        .write(to: URL(fileURLWithPath: CommandLine.arguments[4]))
}

// Export native pixels and the public hit-test rectangles for the interactive web demo.
if CommandLine.arguments.count > 3 && !CommandLine.arguments[3].hasPrefix("-") {
    let destination = URL(fileURLWithPath: CommandLine.arguments[3])
    func capture(_ view: NSView) -> Data {
        let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(ceil(view.bounds.width * 2)), pixelsHigh: Int(ceil(view.bounds.height * 2)), bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
        rep.size = view.bounds.size
        view.cacheDisplay(in: view.bounds, to: rep)
        return rep.representation(using: .png, properties: [:])!
    }
    func action(section: Int, row: Int, key: Int?, text: String) -> String {
        switch section {
        case 0:
            if row == 0 { return key == 0 ? "previous" : "next" }
            if row == 1 { return key == 0 ? "up" : "down" }
            return "desktops"
        case 1:
            if row == 0 { return key == 0 ? "consume-left" : "consume-right" }
            if row == 1 { return key == 0 ? "shrink" : "grow" }
            if row == 2 { return key == 0 ? "height-shrink" : "height-grow" }
            return "focus-pin"
        case 2:
            if text == "…" || key == nil { return row == 0 ? "labels" : "bring" }
            if text == "⇧" { return "bring" }
            return (row == 0 ? "label:" : "bring-label:") + text.uppercased()
        case 3:
            if text == "1–9" { return "send-menu" }
            return ["f":"float", "s":"full", "p":"pin", "j":"join-stack", "x":"leave-stack", "a":"add-pin", "r":"remove-pin", "t":"tile-all", "n":"new-desktop", "d":"delete-desktop", "m":"send-menu"][text.lowercased()] ?? "space"
        default: return row == 0 ? "settings" : "escape"
        }
    }
    var variants: [String: Any] = [:]
    for letters in [false, true] {
        let keys = LeaderHelpView()
        keys.metrics = LeaderHelpView.Metrics(scale: JumpSettings.defaults.keyPanelSize.scale)
        keys.sections = LeaderCommand.help(labels: JumpSettings.defaults.keys(layout: [:]), layout: [:], letters: letters)
        let padding = LeaderHUD.padding, size = keys.intrinsicContentSize
        keys.frame = CGRect(origin: CGPoint(x: padding, y: padding), size: size)
        let frame = PixelPanelView(frame: CGRect(origin: .zero, size: CGSize(width: size.width + 2 * padding, height: size.height + 2 * padding)))
        frame.pixel = keys.metrics.pixel; frame.addSubview(keys)
        if letters { frame.highlight = keys.convert(keys.frame(ofSection: 3), to: frame).insetBy(dx: -keys.metrics.rowGap, dy: -keys.metrics.rowGap) }
        let suffix = letters ? "space" : "main", stem = destination.deletingPathExtension().path + "-" + suffix
        try capture(frame).write(to: URL(fileURLWithPath: stem + ".png"))
        var regions: [[String: Any]] = []
        for (index, hit) in keys.targets().enumerated() {
            let row = keys.sections[hit.target.section].rows[hit.target.row]
            let text = hit.target.key.map { row.keys[$0] } ?? row.title
            let rect = hit.frame.offsetBy(dx: padding, dy: padding)
            let entry: [String: Any] = ["action": action(section: hit.target.section, row: hit.target.row, key: hit.target.key, text: hit.target.key.map { row.keys[$0] } ?? row.keys.first ?? text), "label": row.title + " " + text, "section": hit.target.section, "row": hit.target.row, "title": hit.target.key == nil, "rect": [rect.minX, rect.minY, rect.width, rect.height]]
            regions.append(entry)
            if hit.target.key != nil {
                keys.chosen = hit.click
                try capture(frame).write(to: URL(fileURLWithPath: stem + "-lit-\(index).png"))
                keys.chosen = nil
            }
        }
        variants[suffix] = ["width": frame.bounds.width, "height": frame.bounds.height, "regions": regions]
    }
    try JSONSerialization.data(withJSONObject: variants, options: [.prettyPrinted, .sortedKeys])
        .write(to: destination.deletingPathExtension().appendingPathExtension("json"))
    var barMetrics: [String: Any] = [:]
    final class DeckMarkView: NSView {
        var mark = "PIN DECK"
        override var isFlipped: Bool { true }
        override func draw(_ dirtyRect: NSRect) {
            TabVisualMetrics(iconSize: 48).shortcutNumberMetrics
                .drawMark(mark, in: bounds, flipped: isFlipped, bottom: 8)
        }
    }
    for deck in ["pin", "sky", "max"] {
        let view = DeckMarkView(frame: NSRect(x: 0, y: 0, width: 72, height: 56))
        view.mark = "\(deck.uppercased()) DECK"
        try capture(view).write(to: destination.deletingLastPathComponent().appendingPathComponent("deck-\(deck).png"))
    }
    for size in stride(from: 18, through: 30, by: 2) {
        let m = TabVisualMetrics(iconSize: CGFloat(size))
        let height = m.barHeight(minimum: 22)
        let bounds = CGRect(x: 0, y: 0, width: m.itemWidth, height: height)
        let icon = m.iconFrame(in: bounds, flipped: true, highlighted: false)
        let number = m.numberSquare(in: bounds, flipped: true)
        let mark = m.shortcutNumberMetrics
        barMetrics[String(size)] = ["height": height, "itemWidth": m.itemWidth, "deckItemWidth": m.deckItemWidth, "groupGap": m.groupGap, "currentSlotWidth": m.itemWidth * m.currentSlotScale,
            "iconTop": icon.minY, "iconSize": icon.width, "lensScale": TabVisualMetrics.lensIconScale(for: CGFloat(size)),
            "numberX": number.minX, "numberY": number.minY, "numberSide": number.width, "numberPixel": m.numberPixel,
            "markWidth": mark.markWidth("PIN DECK"), "markHeight": mark.markBlockHeight("PIN DECK"), "markPixel": mark.markPixel, "baseline": m.trayBaseline]
    }
    try JSONSerialization.data(withJSONObject: barMetrics, options: [.prettyPrinted, .sortedKeys])
        .write(to: destination.deletingLastPathComponent().appendingPathComponent("tab-metrics.json"))
    for active in [false, true] {
        let map = DesktopLayoutMapView(frame: CGRect(x: 0, y: 0, width: 54, height: 30))
        map.metrics = TabVisualMetrics(iconSize: 30); map.short = true; map.leaderActive = active
        map.area = CGRect(x: 0, y: 0, width: 1512, height: 920)
        var cells: [DesktopLayoutMapView.Cell] = []
        for index in 0..<7 {
            let x = CGFloat(86) + CGFloat(index - 3) * CGFloat(1352)
            let rect = CGRect(x: x, y: 8, width: 1340, height: 904)
            cells.append(DesktopLayoutMapView.Cell(id: .window(CGWindowID(index + 1)), frame: rect, focused: index == 3))
        }
        map.setWindows(cells, animated: false)
        try capture(map).write(to: destination.deletingLastPathComponent().appendingPathComponent(active ? "map-leader.png" : "map-normal.png"))
    }
}
