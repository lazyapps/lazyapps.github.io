import AppKit

@main enum ExportMenubar {
    static func main() throws {
        _ = NSApplication.shared
        let output = URL(fileURLWithPath: CommandLine.arguments.last!)
        let image = StatusIcon.image(for: .active)
        let bitmap = image.representations.compactMap { $0 as? NSBitmapImageRep }.first { $0.pixelsHigh == Int(image.size.height * 2) }!
        try bitmap.representation(using: .png, properties: [:])!.write(to: output)
        for (symbol, filename, size) in [
            ("apple.logo", "doze-system-apple.png", NSSize(width: 14, height: 17)),
            ("wifi", "doze-system-wifi.png", NSSize(width: 17, height: 14)),
            ("battery.100percent", "doze-system-battery.png", NSSize(width: 23, height: 12))
        ] {
            let symbolImage = NSImage(systemSymbolName: symbol, accessibilityDescription: nil)!
                .withSymbolConfiguration(NSImage.SymbolConfiguration(pointSize: 16, weight: .medium))!
            let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(size.width * 2),
                pixelsHigh: Int(size.height * 2), bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true,
                isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
            bitmap.size = size
            NSGraphicsContext.saveGraphicsState()
            NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
            symbolImage.draw(in: NSRect(origin: .zero, size: size))
            NSGraphicsContext.restoreGraphicsState()
            try bitmap.representation(using: .png, properties: [:])!.write(to: output.deletingLastPathComponent().appendingPathComponent(filename))
        }
    }
}
