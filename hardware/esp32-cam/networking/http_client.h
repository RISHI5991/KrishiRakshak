#ifndef HTTP_CLIENT_H
#define HTTP_CLIENT_H

#include <WiFi.h>
#include <HTTPClient.h>

String sendImageToServer(uint8_t* jpegBuf, size_t jpegLen, const char* serverUrl) {
    if (WiFi.status() != WL_CONNECTED) {
        return "Error: WiFi not connected";
    }

    HTTPClient http;
    String boundary = "----Esp32CamBoundary";
    String contentType = "multipart/form-data; boundary=" + boundary;

    String bodyStart = "--" + boundary + "\r\n";
    bodyStart += "Content-Disposition: form-data; name=\"image\"; filename=\"capture.jpg\"\r\n";
    bodyStart += "Content-Type: image/jpeg\r\n\r\n";
    
    String bodyEnd = "\r\n--" + boundary + "--\r\n";

    size_t contentLength = bodyStart.length() + jpegLen + bodyEnd.length();
    
    http.begin(serverUrl);
    http.addHeader("Content-Type", contentType);
    
    uint8_t *full_buffer = (uint8_t *)malloc(contentLength);
    if (!full_buffer) {
        return "Error: memory alloc failed";
    }
    
    memcpy(full_buffer, bodyStart.c_str(), bodyStart.length());
    memcpy(full_buffer + bodyStart.length(), jpegBuf, jpegLen);
    memcpy(full_buffer + bodyStart.length() + jpegLen, bodyEnd.c_str(), bodyEnd.length());
    
    int httpResponseCode = http.POST(full_buffer, contentLength);
    String response = "";
    
    if (httpResponseCode > 0) {
        response = http.getString();
    } else {
        response = "Error code: " + String(httpResponseCode);
    }
    
    free(full_buffer);
    http.end();
    return response;
}

#endif
