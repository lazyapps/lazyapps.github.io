import AppKit

func svgPath(_ path: CGPath) -> String {
    var commands: [String] = []
    func point(_ value: CGPoint) -> String { "\(value.x) \(value.y)" }
    path.applyWithBlock { pointer in
        let element = pointer.pointee
        switch element.type {
        case .moveToPoint: commands.append("M\(point(element.points[0]))")
        case .addLineToPoint: commands.append("L\(point(element.points[0]))")
        case .addQuadCurveToPoint: commands.append("Q\(point(element.points[0])) \(point(element.points[1]))")
        case .addCurveToPoint: commands.append("C\(point(element.points[0])) \(point(element.points[1])) \(point(element.points[2]))")
        case .closeSubpath: commands.append("Z")
        @unknown default: fatalError("Unsupported native path element")
        }
    }
    return commands.joined(separator: " ")
}

@main enum ExportMenubar {
    static func main() throws {
        _ = NSApplication.shared
        let output = URL(fileURLWithPath: CommandLine.arguments.last!)
        for (state, keepAwake, filename) in [
            (StatusIcon.State.active, false, output.lastPathComponent),
            (.active, true, "doze-menubar-keep-awake.png"),
            (.paused, false, "doze-menubar-paused.png"),
            (.paused, true, "doze-menubar-paused-keep-awake.png")
        ] {
            let image = StatusIcon.image(for: state, keepAwake: keepAwake)
            let bitmap = image.representations.compactMap { $0 as? NSBitmapImageRep }.first { $0.pixelsHigh == Int(image.size.height * 2) }!
            try bitmap.representation(using: .png, properties: [:])!.write(to: output.deletingLastPathComponent().appendingPathComponent(filename))
            let bounds = StatusIcon.vectorPathForExport(smiling: false).boundingBoxOfPath
            let path = svgPath(StatusIcon.vectorPathForExport(smiling: keepAwake))
            let svg = """
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="20" viewBox="0 0 22 20"><g transform="translate(11 10) scale(0.8 -0.8) translate(\(-bounds.midX) \(-bounds.midY))" fill="#000000" opacity="\(state == .paused ? 0.45 : 1)"><path d="\(path)"/></g></svg>
            """
            try svg.write(to: output.deletingLastPathComponent().appendingPathComponent(filename).deletingPathExtension().appendingPathExtension("svg"), atomically: true, encoding: .utf8)
        }
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
