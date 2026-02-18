import Foundation
import UIKit
import Combine

/// Manages MJPEG stream from HTTP source and still image capture
class NetworkCameraManager: NSObject, ObservableObject {
  @Published var isStreaming = false
  var onFrameCaptured: ((UIImage) -> Void)?
  var onImageCaptured: ((UIImage) -> Void)?
  var onError: ((String) -> Void)?

  // Configurable URLs - can be updated via settings if needed
  var streamURL: URL?
  var captureURL: URL?

  private var session: URLSession?
  private var dataTask: URLSessionDataTask?
  private let frameBoundary = "--123456789000000000000987654321" // Standard boundary often used, but we'll adapt
  private var buffer = Data()
  
  init(host: String = "localhost") {
    let cleanHost = host.isEmpty ? "localhost" : host
    self.streamURL = URL(string: "http://\(cleanHost):81/stream")
    self.captureURL = URL(string: "http://\(cleanHost)/capture")

    super.init()
    let config = URLSessionConfiguration.default
    config.timeoutIntervalForRequest = TimeInterval.infinity // Keep stream open
    config.timeoutIntervalForResource = TimeInterval.infinity
    self.session = URLSession(configuration: config, delegate: self, delegateQueue: nil)
  }

  func start() {
    guard !isStreaming, let url = streamURL else { return }
    
    NSLog("[NetworkCamera] Starting stream from %@", url.absoluteString)
    isStreaming = true
    
    var request = URLRequest(url: url)
    request.timeoutInterval = TimeInterval.infinity
    
    dataTask = session?.dataTask(with: request)
    dataTask?.resume()
  }

  func stop() {
    guard isStreaming else { return }
    
    NSLog("[NetworkCamera] Stopping stream")
    isStreaming = false
    dataTask?.cancel()
    dataTask = nil
  }
  
  func captureStillImage() {
    guard let url = captureURL else { return }
    
    NSLog("[NetworkCamera] Capturing still from %@", url.absoluteString)
    
    let task = URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
      if let error = error {
        self?.onError?(error.localizedDescription)
        return
      }
      
      guard let data = data, let image = UIImage(data: data) else {
        self?.onError?("Failed to decode image data")
        return
      }
      
      DispatchQueue.main.async {
        self?.onImageCaptured?(image)
      }
    }
    task.resume()
  }
}


// MARK: - URLSessionDataDelegate
extension NetworkCameraManager: URLSessionDataDelegate {
  
  func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
    self.buffer.append(data)
    self.processBuffer()
  }
  
  func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
    if let error = error {
       // Check if it was cancelled intentionally
       let nsError = error as NSError
       if nsError.code == NSURLErrorCancelled {
         NSLog("[NetworkCamera] Stream stopped by user")
         return
       }
       
       NSLog("[NetworkCamera] Stream error: %@", error.localizedDescription)
       DispatchQueue.main.async { [weak self] in
         self?.onError?(error.localizedDescription)
         self?.isStreaming = false
       }
    } else {
       NSLog("[NetworkCamera] Stream closed unexpectedly")
       DispatchQueue.main.async { [weak self] in
         self?.isStreaming = false
       }
    }
  }

  private func processBuffer() {
    // Scan for JPEG frames: SOI (FF D8) ... EOI (FF D9)
    
    while true {
       // Find Start of Image
       guard let soiRange = buffer.range(of: Data([0xFF, 0xD8])) else {
          // If buffer is getting too large without finding a start, clear it to free memory
          if buffer.count > 10_000_000 {
             buffer.removeAll()
          }
          return // Need more data
       }
       
       // Search for End of Image after the start
       let searchRange = soiRange.upperBound..<buffer.count
       guard let eoiRange = buffer.range(of: Data([0xFF, 0xD9]), options: [], in: searchRange) else {
          return // Frame not complete yet
       }
       
       let verifiedEndIndex = eoiRange.upperBound
       
       // Extract the frame data
       let frameData = buffer[soiRange.lowerBound..<verifiedEndIndex]
       
       // Try to create image
       if let image = UIImage(data: frameData) {
          DispatchQueue.main.async { [weak self] in
             self?.onFrameCaptured?(image)
          }
       }
       
       // Remove processed frame from buffer
       buffer.removeSubrange(0..<verifiedEndIndex)
    }
  }
}
