"""
Error handling middleware.
"""
from flask import jsonify


class ErrorHandler:
    """Error handler middleware for consistent error responses."""
    
    @staticmethod
    def handle_validation_error(error):
        """Handle validation errors."""
        return jsonify({"error": str(error)}), 400
    
    @staticmethod
    def handle_not_found(error):
        """Handle not found errors."""
        return jsonify({"error": "Resource not found"}), 404
    
    @staticmethod
    def handle_server_error(error):
        """Handle server errors."""
        return jsonify({"error": "Internal server error"}), 500
