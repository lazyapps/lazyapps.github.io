import AppKit
import Foundation
import SwiftUI
import YiYanCore
@testable import YiYanUI

// Render the selected real record and isolated settings with the app's own resources.
@main
struct YiloWebsiteCapture {
@MainActor static func main() async throws {
    let tag = ProcessInfo.processInfo.environment["YILO_CAPTURE_LOCALE"]!
    _ = NSApplication.shared
    let labels = ["language.notes", "record.example", "advice.kind.learning_point", "advice.category.collocation", "advice.category.translation_pattern", "language.section", "language.targets", "language.search", "language.japanese_reading.help"]
    for key in labels {
        let expected = AppLocalization.string(key, localizationIdentifier: tag)
        precondition(expected != key && AppLocalization.string(key) == expected, "Native localization did not match requested language: \(key)")
    }
    let output = URL(filePath: ProcessInfo.processInfo.environment["YILO_CAPTURE_DIR"]!)
    let recordURL = URL(filePath: ProcessInfo.processInfo.environment["YILO_CAPTURE_RECORD"]!)
    let decoder = JSONDecoder()
    decoder.dateDecodingStrategy = .secondsSince1970
    let record = try decoder.decode(LearningRecord.self, from: Data(contentsOf: recordURL))
    precondition(record.configuration.sourceLanguage.rawValue == tag)
    let data = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: data) }
    let settings = AppSettingsViewModel(repository: SettingsRepository(fileURL: data.appending(path: "settings.json")))
    settings.setSourceLanguage(.init(rawValue: tag))
    settings.setTargetLanguages(record.configuration.targetLanguages)
    settings.setJapaneseReadingStyle(.romaji)
    settings.setChineseReadingStyle(.pinyin, for: .simplified)
    func capture<V: View>(_ view: V, name: String, dark: Bool = false) async throws {
        NSApp.appearance = NSAppearance(named: dark ? .darkAqua : .aqua)
        let host = NSHostingView(rootView: view
            .environment(\.colorScheme, dark ? .dark : .light)
            .environment(\.locale, Locale(identifier: tag))
            .environment(\.layoutDirection, tag == "ar" ? .rightToLeft : .leftToRight)
            .background(Color(nsColor: .windowBackgroundColor)))
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 620, height: 900), styleMask: [], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        window.contentView = host
        defer { window.close() }
        for _ in 0..<80 {
            try await Task.sleep(for: .milliseconds(25))
            host.frame.size = host.fittingSize
            host.layoutSubtreeIfNeeded()
        }
        window.setContentSize(host.fittingSize)
        host.layoutSubtreeIfNeeded()
        let bitmap = host.bitmapImageRepForCachingDisplay(in: host.bounds)!
        host.cacheDisplay(in: host.bounds, to: bitmap)
        try bitmap.representation(using: .png, properties: [:])!.write(to: output.appending(path: name))
    }
    try await capture(RecordCardView(record: record, japaneseReadingStyle: .romaji, chineseReadings: .init(simplified: .pinyin, traditional: .zhuyin), learningNotesExpanded: true, bookmark: {}, chat: {}, delete: {}).frame(width: 744), name: "learning-record.png", dark: true)
    try await capture(Form {
        Section(AppLocalization.string("language.section")) { LearningLanguageSettingsView(settings: settings) }
    }.formStyle(.grouped).frame(width: 620, height: 440), name: "learning-settings.png")
    try await capture(LanguageSelectionView(settings: settings, multiple: true), name: "language-selection.png")
    let receipt: [String: Any] = ["requestedLocale": tag, "nativeLocale": AppLocalization.currentLocale.identifier,
        "sourceLanguage": settings.settings.translation.sourceLanguage.rawValue,
        "targetLanguages": settings.settings.translation.targetLanguages.map(\.rawValue),
        "labels": Dictionary(uniqueKeysWithValues: labels.map { ($0, AppLocalization.string($0)) }),
        "operatingSystem": ProcessInfo.processInfo.operatingSystemVersionString]
    try JSONSerialization.data(withJSONObject: receipt, options: [.prettyPrinted, .sortedKeys]).write(to: output.appending(path: "locale.json"))
}
}
