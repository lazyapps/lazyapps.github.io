import AppKit
let destination = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let identifiers = ["finder": "com.apple.finder", "safari": "com.apple.Safari", "notes": "com.apple.Notes", "mail": "com.apple.mail", "calendar": "com.apple.iCal", "terminal": "com.apple.Terminal", "music": "com.apple.Music"]
for (name, identifier) in identifiers {
    guard let application = NSWorkspace.shared.urlForApplication(withBundleIdentifier: identifier) else { fatalError(identifier) }
    let image = NSWorkspace.shared.icon(forFile: application.path)
    let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: 128, pixelsHigh: 128, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
    image.draw(in: NSRect(x: 0, y: 0, width: 128, height: 128), from: .zero, operation: .copy, fraction: 1)
    NSGraphicsContext.restoreGraphicsState()
    try bitmap.representation(using: .png, properties: [:])!.write(to: destination.appendingPathComponent("\(name).png"))
}
