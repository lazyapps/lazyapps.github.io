import AppKit

enum StatusIcon {
    enum State: CaseIterable, Hashable {
        case active, dimmed, paused, media, attention
    }

    private struct Variant: Hashable {
        let state: State
        let keepAwake: Bool
    }

    private static let images = Dictionary(uniqueKeysWithValues: State.allCases.flatMap { state in
        [false, true].map { awake in
            (Variant(state: state, keepAwake: awake), makeImage(state: state, keepAwake: awake))
        }
    })

    static func image(for state: State, keepAwake: Bool = false) -> NSImage {
        images[Variant(state: state, keepAwake: keepAwake)]!
    }

    private static func makeImage(state: State, keepAwake: Bool) -> NSImage {
        let size = NSSize(width: 22, height: 20)
        let image = NSImage(size: size)
        let glyph = monogram(smiling: keepAwake)
        let bounds = monogram(smiling: false).boundingBoxOfPath
        for scale in [1, 2] {
            let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil,
                pixelsWide: 22 * scale, pixelsHigh: 20 * scale,
                bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
            bitmap.size = size
            NSGraphicsContext.saveGraphicsState()
            NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
            let context = NSGraphicsContext.current!.cgContext
            context.setShouldAntialias(true)
            context.saveGState()
            context.translateBy(x: size.width / 2, y: size.height / 2)
            context.scaleBy(x: 0.8, y: 0.8)
            context.translateBy(x: -bounds.midX, y: -bounds.midY)
            let opacity: CGFloat = state == .paused ? 0.45 : state == .media ? 0.75 : 1
            context.setFillColor(NSColor.black.withAlphaComponent(opacity).cgColor)
            context.addPath(glyph)
            context.fillPath()
            context.restoreGState()
            if state == .media {
                context.saveGState()
                context.setBlendMode(.clear)
                context.fillEllipse(in: CGRect(x: 6, y: 5, width: 10, height: 10))
                context.setBlendMode(.normal)
                context.setFillColor(NSColor.black.withAlphaComponent(0.9).cgColor)
                context.fillEllipse(in: CGRect(x: 7, y: 6, width: 8, height: 8))
                let play = CGMutablePath()
                play.move(to: CGPoint(x: 10, y: 8))
                play.addLine(to: CGPoint(x: 13, y: 10))
                play.addLine(to: CGPoint(x: 10, y: 12))
                play.closeSubpath()
                context.setBlendMode(.clear)
                context.addPath(play)
                context.fillPath()
                context.restoreGState()
            }
            NSGraphicsContext.restoreGraphicsState()
            image.addRepresentation(bitmap)
        }
        image.isTemplate = true
        return image
    }

    private static func monogram(smiling: Bool) -> CGPath {
        let eye = CGMutablePath()
        eye.addRoundedRect(in: CGRect(x: 2, y: 3, width: 4, height: 12),
                           cornerWidth: 1, cornerHeight: 1)
        eye.move(to: CGPoint(x: 2, y: 11))
        eye.addLine(to: CGPoint(x: 6, y: 11))
        eye.move(to: CGPoint(x: 2, y: 7))
        eye.addLine(to: CGPoint(x: 6, y: 7))

        let light = CGMutablePath()
        light.move(to: CGPoint(x: 14, y: 1))
        light.addLine(to: CGPoint(x: 14, y: 15))
        light.move(to: CGPoint(x: 9, y: 9))
        light.addLine(to: CGPoint(x: 20, y: 9))
        light.move(to: CGPoint(x: 14, y: 9))
        light.addLine(to: CGPoint(x: 9, y: 3))
        light.move(to: CGPoint(x: 14, y: 9))
        light.addLine(to: CGPoint(x: 19, y: 3))
        let leftEyeY: CGFloat = smiling ? 13 : 14
        light.move(to: CGPoint(x: 9, y: leftEyeY))
        light.addQuadCurve(to: CGPoint(x: 11, y: leftEyeY), control: CGPoint(x: 10, y: smiling ? 15 : 12))
        let rightEyeY: CGFloat = smiling ? 12.75 : 14
        light.move(to: CGPoint(x: 17, y: rightEyeY))
        light.addQuadCurve(to: CGPoint(x: 20, y: rightEyeY), control: CGPoint(x: 18.5, y: smiling ? 15.25 : 11.5))
        return eye.copy(strokingWithWidth: 2, lineCap: .round, lineJoin: .round, miterLimit: 1)
            .union(light.copy(strokingWithWidth: 2, lineCap: .round, lineJoin: .round, miterLimit: 1))
    }
}
