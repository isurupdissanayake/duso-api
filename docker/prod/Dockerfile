FROM excel-data-processor-base:latest

# Production environment variables
ENV ENVIRONMENT=production \
    DEBUG=false \
    LOG_LEVEL=info

# Copy the application code
COPY --chown=appuser:appuser . .

# Command to run the application in production mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"] 