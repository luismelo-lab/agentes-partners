// OCR local (framework Vision do macOS): nada sai da máquina. Uso: ocr <imagem|pdf>
import Foundation
import Vision
import AppKit
import PDFKit

func textoDe(_ cg: CGImage) -> String {
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate; req.recognitionLanguages = ["pt-BR"]; req.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    return (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}
let url = URL(fileURLWithPath: CommandLine.arguments[1])
var saida: [String] = []
if let pdf = PDFDocument(url: url) {
    for i in 0..<pdf.pageCount {
        guard let p = pdf.page(at: i) else { continue }
        let r = p.bounds(for: .mediaBox); let esc: CGFloat = 2
        let img = NSImage(size: NSSize(width: r.width * esc, height: r.height * esc))
        img.lockFocus(); NSColor.white.set(); NSRect(origin: .zero, size: img.size).fill()
        let ctx = NSGraphicsContext.current!.cgContext; ctx.scaleBy(x: esc, y: esc); p.draw(with: .mediaBox, to: ctx); img.unlockFocus()
        if let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) { saida.append(textoDe(cg)) }
    }
} else if let img = NSImage(contentsOf: url), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) {
    saida.append(textoDe(cg))
}
print(saida.joined(separator: "\n\n"))
