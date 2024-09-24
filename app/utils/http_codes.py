import logging

HTTP_CODES = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found. The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
    405: "Method Not Allowed",
    500: "Internal Server Error",
    503: "Service Unavailable"
}

def get_http_message(status_code):
    try:
        return HTTP_CODES.get(status_code, "Unknown Status")
    except Exception as e:
        logging.error(f"Error retrieving HTTP message: {e}")
        return "Internal Server Error"
