import AppKit

// CoreText-backed AppKit shaping preserves Arabic joining and Indic clusters.
let args = CommandLine.arguments
let configURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2], isDirectory: true)
let entries = try JSONSerialization.jsonObject(with: Data(contentsOf: configURL)) as! [[String: Any]]
try FileManager.default.createDirectory(at: outputURL, withIntermediateDirectories: true)
for entry in entries {
    let width = entry["width"] as! Int, height = entry["height"] as! Int
    let image = NSImage(size: NSSize(width: width, height: height))
    image.lockFocus()
    NSColor.clear.setFill()
    NSRect(x: 0, y: 0, width: width, height: height).fill(using: .copy)
    let text = entry["text"] as! String
    let rgb = entry["color"] as! [Double]
    let color = NSColor(srgbRed: rgb[0], green: rgb[1], blue: rgb[2], alpha: 1)
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = entry["align"] as? String == "center" ? .center : entry["rtl"] as? Bool == true ? .right : .left
    paragraph.baseWritingDirection = entry["rtl"] as? Bool == true ? .rightToLeft : .leftToRight
    paragraph.lineBreakMode = .byWordWrapping
    paragraph.lineSpacing = 4
    var size = entry["size"] as! Double
    let weight: NSFont.Weight = entry["bold"] as? Bool == true ? .semibold : .regular
    var attributes: [NSAttributedString.Key: Any] = [:]
    while size >= 18 {
        attributes = [.font: NSFont.systemFont(ofSize: size, weight: weight), .foregroundColor: color, .paragraphStyle: paragraph]
        let bound = (text as NSString).boundingRect(with: NSSize(width: width - 4, height: 10000), options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: attributes)
        let explicitLinesFit = !text.contains("\n") || text.components(separatedBy: "\n").allSatisfy {
            ($0 as NSString).size(withAttributes: attributes).width <= Double(width - 8)
        }
        if explicitLinesFit && bound.height <= Double(height - 16) && bound.width <= Double(width - 4) { break }
        size -= 1
    }
    (text as NSString).draw(with: NSRect(x: 2, y: 2, width: width - 4, height: height - 4), options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: attributes)
    image.unlockFocus()
    let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
    try bitmap.representation(using: .png, properties: [:])!.write(to: outputURL.appendingPathComponent(entry["file"] as! String))
}
