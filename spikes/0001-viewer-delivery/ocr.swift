// Print the text macOS's Vision framework reads in an image, one line per text box, top to bottom.
// Used by android_flip.py where the card's web view is hidden from Android's accessibility tree.
// Build: swiftc -O ocr.swift -o <somewhere>/rs-ocr
import Foundation
import Vision

let url = URL(fileURLWithPath: CommandLine.arguments[1])
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
try VNImageRequestHandler(url: url).perform([request])
for obs in (request.results ?? []).sorted(by: { $0.boundingBox.minY > $1.boundingBox.minY }) {
    if let text = obs.topCandidates(1).first?.string {
        let b = obs.boundingBox
        print(String(format: "%.3f\t%.3f\t%@", b.midX, 1 - b.midY, text))
    }
}
